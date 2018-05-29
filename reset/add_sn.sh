#!/bin/bash

cd

docker-compose exec telemarket-old python manage.py shell<<EOF
user = User.query.filter_by(username=$1).first()
autocommit=True
user.password=$2
db.session.add(user)
db.session.commit()
EOF

