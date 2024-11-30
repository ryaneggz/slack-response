#!/bin/bash

# Step 1: Set the image tag (default to "latest" if not provided)
IMAGE_TAG=${1:-latest}
REPO_OWNER="ryaneggz"
REPO_NAME="slack-agent"
IMAGE_NAME="${REPO_OWNER}/${REPO_NAME}:${IMAGE_TAG}"
CONTAINER_NAME="slack_agent"

echo "Using image: $IMAGE_NAME"

# Step 2: Pull the specified image tag
echo "Pulling the specified image..."
docker pull $IMAGE_NAME || { echo "Failed to pull image"; exit 1; }

# Step 3: Rename the current container (if it exists) for backup
echo "Preparing backup of current container..."
if docker ps -a | grep -q slack-agent; then
    docker rename $CONTAINER_NAME $CONTAINER_NAME-backup || true
    docker stop $CONTAINER_NAME-backup || true
fi

# Step 4: Start the new container with docker run
echo "Starting the new $CONTAINER_NAME container..."
if docker run -d \
    --name $CONTAINER_NAME \
    --restart always \
    -p 5000:5000 \
    --env-file .env \
    $IMAGE_NAME; then
    
    # Step 5: Verify the new container is running properly
    echo "Waiting for container health check..."
    sleep 10  # Wait for container to initialize
    
    if docker ps | grep -q $CONTAINER_NAME; then
        echo "New container is running successfully"
        
        # Clean up the backup container and old images
        echo "Cleaning up backup and old images..."
        docker rm $CONTAINER_NAME-backup || true
        
        # # Clean up images older than 24 hours, excluding the current one
        # docker images --format "{{.ID}} {{.CreatedAt}}" ryaneggz/slack-agent | \
        # awk -v image="$IMAGE_NAME" '$0 !~ image {cmd="date -d\""$2" "$3"\" +%s"; cmd | getline created; \
        # if (systime()-created > 86400) {print $1}}' | \
        # xargs -r docker rmi || true
        
        echo "Deployment successful!"
    else
        echo "New container failed to start properly. Rolling back..."
        docker stop $CONTAINER_NAME || true
        docker rm $CONTAINER_NAME || true
        docker rename $CONTAINER_NAME-backup $CONTAINER_NAME || true
        docker start $CONTAINER_NAME || true
        echo "Rollback completed. Previous version restored."
        exit 1
    fi
else
    echo "Failed to start new container. Rolling back..."
    docker rename $CONTAINER_NAME-backup $CONTAINER_NAME || true
    docker start $CONTAINER_NAME || true
    echo "Rollback completed. Previous version restored."
    exit 1
fi

echo "Slack-agent container has been successfully updated and is set to restart always."