import datetime
import json
import requests
from config import MINIO_ADDR, MINIO_UID, MINIO_KEY, MINIO_BUCKET, RECORD_PATH, ERROR_PATH, BACKUP_PATH, RETRY_TIME, \
    POST_URL, POST_TOKEN
import datetime
import time
import os
import io
import logging
import tarfile
import shutil
import logging.handlers
import time

from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
from multiprocessing import cpu_count, Pool

log = logging.getLogger('record-parser')
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s:%(filename)s:%(funcName)-6s %(message)s')

fh = logging.handlers.TimedRotatingFileHandler("/log/record/record-parser.log", "midnight", backupCount=20)
fh.setFormatter(formatter)
log.addHandler(fh)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

timeout = (5, 10)

# Initialize minioClient with an endpoint and access/secret keys.
minioClient = Minio(MINIO_ADDR,
                    access_key=MINIO_UID,
                    secret_key=MINIO_KEY,
                    secure=False)


def log_to_json(recordpath_root, unpackdir, logname):
    log_date = ""
    jsoncout = []
    logpath = "%s/%s/%s" % (recordpath_root, unpackdir, logname)
    has_date = False
    file_name = logname.split(".")[0]
    file_infos = file_name.split("_")
    task_id = file_infos[0]
    call_number = file_infos[1]
    called_number = file_infos[2]
    sum_record_name = called_number + "_" + task_id + "_" + call_number + ".mp3"
    suc = False
    if logpath.endswith('.log'):
        with open(logpath, "r") as logfile:
            for line in logfile:
                # self._parser(line)
                if not line.startswith("#"):
                    tline = {}
                    for i in line.split("#"):
                        p = i.split("@")
                        if p[0] == "duration":
                            tline[p[0]] = int(p[1])
                        elif p[0] == "time" and not has_date:
                            datetime_object = datetime.datetime.strptime(p[1], '%Y-%m-%d %H:%M:%S.%f')
                            log_date = datetime_object.strftime('%Y%m%d')
                            has_date = True
                        elif p[0] == "file" and p[1]:
                            mp3filename = p[1]
                            mp3filepath = "%s/%s/%s" % (recordpath_root, unpackdir, mp3filename)
                            uri = "%s/%s/%s" % (log_date, unpackdir, mp3filename)
                            suc = oss_save(mp3filepath, uri)
                            if not suc:
                                return None
                            tline["file"] = uri
                        elif len(p) > 1:
                            tline[p[0]] = p[1]
                    jsoncout.append(tline)
    else:
        log.error("not log file")

    mp3filepath = "%s/%s/%s" % (recordpath_root, unpackdir, sum_record_name)
    uri = "%s/%s/%s" % (log_date, unpackdir, sum_record_name)
    suc = oss_save(mp3filepath, uri)
    if not suc:
        return None
    if not jsoncout:
        log.Warn("log no content")
        return None
    jsoncout[0]["file"] = uri

    uri = "%s/%s/%s" % (log_date, unpackdir, "record.json")
    data = json.dumps(jsoncout)

    suc = oss_save_str(data, uri)
    if not suc:
        return None
    return uri


def oss_save(file_path, uri):
    # Put an object 'pumaserver_debug.log' with contents from 'pumaserver_debug.log'.
    suc = False
    if not os.path.exists(file_path):
        log.error(file_path + " file not existed")
        return suc
    state_info = None
    try:
        state_info = minioClient.stat_object(MINIO_BUCKET, uri)
        if state_info.size > 0:
            log.info("existed uri: " + uri)
            return True
    except Exception as err:
        # log.error("state error: " + str(type(err)))
        pass

    for i in range(2):
        try:
            minioClient.fput_object(MINIO_BUCKET, uri, file_path)
            suc = True
        except Exception as err:
            log.error("put object failed, uri: " + uri + " exception type: " + str(type(err)))
            time.sleep(2)
    return suc


def oss_save_str(data_str, uri):
    data_bytes = data_str.encode("utf-8")
    data_len = len(data_bytes)
    jsonio = io.BytesIO(data_bytes)
    suc = False
    # Put an object 'pumaserver_debug.log' with contents from 'pumaserver_debug.log'.
    try:
        state_info = minioClient.stat_object(MINIO_BUCKET, uri)
        if state_info.size > 0:
            return True
    except Exception as err:
        log.error("state error: " + str(type(err)))

    for i in range(3):
        try:

            minioClient.put_object(MINIO_BUCKET, uri, jsonio, data_len, content_type="application/json")
            jsonio.close()
            suc = True
        except Exception as err:
            log.error("put object failed, uri: " + uri + " exception type: " + str(type(err)))
            jsonio.close()
            time.sleep(2)

    return suc


def save(file_obj, meta=None):
    headers = {}
    if meta:
        if 'mime' in meta:
            headers['Content-Type'] = meta.pop('mime')
        headers.update({'%s-%s' % ("X-Storage", _k.lower()): _v for _k, _v in list(meta.items())})

    res = requests.get("" + "/dir/assign", timeout=timeout)
    if not res.ok:
        res.raise_for_status()
    res_json = res.json()
    log.info(res_json)
    put_url = res_json["publicUrl"] + '/' + res_json["fid"]
    public_url = res_json["publicUrl"] + '/' + res_json["fid"]
    files = {"record": file_obj}
    res = requests.put(
            put_url, files=files, headers=headers, timeout=timeout
    )
    if not res.ok:
        res.raise_for_status()
    return public_url


def getlogfile(unpackdir):
    files = os.listdir("%s/%s" % (RECORD_PATH, unpackdir))
    for fi in files:
        if fi.startswith(unpackdir) and fi.endswith(".log"):
            return fi


def unpackps(args):
    try:
        recordpath_root = args[0]
        tarname = args[1]
        recordpath = "%s/%s" % (recordpath_root, tarname)
        if recordpath.endswith(".tar"):
            modify_time = os.path.getmtime(recordpath)
            cur_time = time.time()
            if cur_time - modify_time < 20:
                return 1
            log.info("now process %s" % (recordpath))
            _retry_times = 0
            unpackdir = tarname[:-4]
            tar = tarfile.open(recordpath)
            try:
                tar.extractall(path=recordpath_root)
                logname = getlogfile(unpackdir)

                jsondata = log_to_json(recordpath_root, unpackdir, logname)
                if not jsondata:
                    shutil.move(recordpath, "%s/%s" % (ERROR_PATH, tarname))
                else:
                    log.info(jsondata)
                    shutil.move(recordpath, "%s/%s" % (BACKUP_PATH, tarname))
                tar.close()
            except Exception as e:
                tar.close()
                log.exception(e)
            log.info("remove tree")
            shutil.rmtree("%s/%s" % (recordpath_root, unpackdir))
            log.info("deal completes")
    except Exception as e:
        log.exception(e)


def deal_record_file():
    make_record_bucket()
    if not os.path.exists(ERROR_PATH):
        os.mkdir(ERROR_PATH)
    if not os.path.exists(BACKUP_PATH):
        os.mkdir(BACKUP_PATH)

    log.info("start process record file")
    cpus = cpu_count()
    pool = Pool(processes=cpus * 2)
    thread_args = [(RECORD_PATH, file) for file in os.listdir(RECORD_PATH) if file.endswith(".tar")]

    try:
        log.info(thread_args)
        result = pool.map(unpackps, thread_args)
        log.info(result)
        pool.close()
        pool.join()

    except Exception as e:
        log.exception(e)
        pool.close()
        pool.join()

    log.info('exec sync groups task complete')


def make_record_bucket():
    try:
        minioClient.make_bucket(MINIO_BUCKET, location="hz")
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise


if __name__ == '__main__':
    while True:
        log.info("---------start once----------")
        deal_record_file()
        log.info("---------start complete----------")
        time.sleep(20)
