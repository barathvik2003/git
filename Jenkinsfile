pipeline {

    agent any

    environment {
        REGISTRY = '127.0.0.1:5001'
        REGISTRY_NAME = 'local-registry'
        APP_NAME = 'company-management'
        CONTAINER_NAME = 'company-management'
        APP_PORT = '5000'
        HOST_PORT = '5000'
    }

    stages {

        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv

                    ./venv/bin/pip install --upgrade pip

                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    ./venv/bin/pip install pytest

                    ./venv/bin/pytest -v
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    ./venv/bin/pip install pip-audit

                    ./venv/bin/pip-audit -r requirements.txt || true
                '''
            }
        }

        stage('Ensure Local Registry') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Checking Local Container Registry"
                    echo "========================================"

                    if ! sudo podman container exists ${REGISTRY_NAME}; then

                        echo "Registry does not exist."
                        echo "Creating local registry..."

                        sudo podman run -d \
                            --name ${REGISTRY_NAME} \
                            -p 127.0.0.1:5001:5000 \
                            --restart=always \
                            docker.io/library/registry:2

                    else

                        echo "Registry container already exists."

                        REGISTRY_RUNNING=$(sudo podman inspect \
                            -f '{{.State.Running}}' \
                            ${REGISTRY_NAME})

                        if [ "$REGISTRY_RUNNING" != "true" ]; then

                            echo "Registry is stopped."
                            echo "Starting registry..."

                            sudo podman start ${REGISTRY_NAME}

                        else

                            echo "Registry is already running."

                        fi
                    fi

                    echo "Waiting for registry..."

                    for i in $(seq 1 10); do

                        if curl --silent --fail \
                            http://127.0.0.1:5001/v2/ > /dev/null; then

                            echo "Registry is READY."
                            break

                        fi

                        echo "Waiting for registry... attempt $i/10"
                        sleep 2

                    done

                    echo "Testing registry connection..."

                    curl --fail \
                        http://127.0.0.1:5001/v2/

                    echo ""
                    echo "Local registry check PASSED."
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                    echo "Building container image..."

                    sudo podman build \
                        -t ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER} .

                    echo "Image build completed."

                    sudo podman images \
                        ${REGISTRY}/${APP_NAME}
                '''
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    echo "Pushing image to local registry..."

                    sudo podman push \
                        --tls-verify=false \
                        ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}

                    echo "Image push completed."
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Deploying Application"
                    echo "========================================"

                    echo "Image:"
                    echo "${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"

                    echo "Stopping old container..."

                    sudo podman stop \
                        ${CONTAINER_NAME} 2>/dev/null || true

                    echo "Removing old container..."

                    sudo podman rm \
                        ${CONTAINER_NAME} 2>/dev/null || true

                    echo "Starting new container..."

                    sudo podman run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${HOST_PORT}:${APP_PORT} \
                        ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}

                    echo "Deployment completed."

                    echo "Current container status:"

                    sudo podman ps \
                        --filter name=${CONTAINER_NAME}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Application Health Check"
                    echo "========================================"

                    echo "Waiting for application..."
                    sleep 5

                    echo "Checking application health..."

                    curl --fail --silent \
                        http://127.0.0.1:${HOST_PORT}/health

                    echo ""
                    echo "Health check PASSED."
                '''
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'CI/CD PIPELINE SUCCESSFUL'
            echo '========================================'

            echo "Application: ${APP_NAME}"
            echo "Image: ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"
            echo "Container: ${CONTAINER_NAME}"
            echo "Application Port: ${HOST_PORT}"
        }

        failure {
            echo '========================================'
            echo 'CI/CD PIPELINE FAILED'
            echo '========================================'

            sh '''
                echo "Registry status:"
                sudo podman ps -a \
                    --filter name=${REGISTRY_NAME}

                echo "Application container status:"
                sudo podman ps -a \
                    --filter name=${CONTAINER_NAME}

                echo "All containers:"
                sudo podman ps -a
            '''
        }

        always {
            echo "Pipeline completed: ${BUILD_NUMBER}"
        }
    }
}
