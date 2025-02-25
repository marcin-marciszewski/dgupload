# #! /bin/bash

# # This shell script quickly deploys your project to your
# # DigitalOcean Droplet

# # generate TAR file from git
# git archive --format tar --output ./project.tar main

# echo 'Uploading project...'
# rsync ./project.tar root@srv12.mikr.us -p 10319:/tmp/project.tar
# echo 'Uploaded complete.'

# echo 'Building image...'
# ssh -o StrictHostKeyChecking=no root@srv12.mikr.us -p 10319 <<'ENDSSH'
#     mkdir -p /app
#     rm -rf /app/* && tar -xf /tmp/project.tar -C /app
#     docker compose -f /app/compose.prod.yml build
# ENDSSH
# echo 'Build complete.'

#! /bin/bash

# This shell script quickly deploys your project to your
# DigitalOcean Droplet

# generate TAR file from git
git archive --format tar --output ./project.tar main

echo 'Uploading project...'
rsync -P -e "ssh -p 10319" ./project.tar root@srv12.mikr.us:/tmp/project.tar
echo 'Upload complete.'

echo 'Building image...'
ssh -o StrictHostKeyChecking=no root@srv12.mikr.us -p 10319 <<'ENDSSH'
    cd /
    # Ensure the tar file exists
    if [ ! -f /tmp/project.tar ]; then
        echo "Error: /tmp/project.tar not found"
        exit 1
    fi
    
    mkdir -p /app
    rm -rf /app/* && tar -xf /tmp/project.tar -C /app
    
    # Check if compose file exists
    if [ ! -f /app/compose.prod.yml ]; then
        echo "Error: /app/compose.prod.yml not found"
        exit 1
    fi
    
    docker compose -f /app/compose.prod.yml build
ENDSSH
echo 'Build complete.'
