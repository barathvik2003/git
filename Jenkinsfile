pipeline {

    agent any

    environment {
        REGISTRY = '127.0.0.1:5001'
        APP_NAME = 'company-management'
        CONTAINER_NAME = 'company-management'
        APP_PORT = '5000'
        HOST_PORT = '5000'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

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

        stage('Build Image') {
            steps {
                sh '''
                    sudo podman build \
                        -t ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    sudo podman push \
                        --tls-verify=false \
                        ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    echo "Deploying ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"

                    sudo podman stop ${CONTAINER_NAME} 2>/dev/null || true
                    sudo podman rm ${CONTAINER_NAME} 2>/dev/null || true

                    sudo podman run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${HOST_PORT}:${APP_PORT} \
                        ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}

                    echo "Deployment completed"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Waiting for application..."
                    sleep 5

                    echo "Checking application health..."

                    curl --fail --silent \
                        http://127.0.0.1:${HOST_PORT}/health

                    echo ""
                    echo "Health check PASSED"
                '''
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'CI/CD PIPELINE SUCCESSFUL'
            echo "Application: ${APP_NAME}"
            echo "Image: ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"
            echo '========================================'
        }

        failure {
            echo '========================================'
            echo 'CI/CD PIPELINE FAILED'
            echo '========================================'

            sh '''
                echo "Checking container status..."
                sudo podman ps -a --filter name=${CONTAINER_NAME}
            '''
        }

        always {
            echo "Pipeline completed: ${BUILD_NUMBER}"
        }
    }
}
