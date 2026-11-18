pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    triggers {
        githubPush()
    }

    environment {
        STUDENT_ID = 'FA23-BDS-055'
        IMAGE      = 'midterm-fa23-bds-055'
        CONTAINER  = 'midterm-api'
        SENDER     = 'sakinaabbas2017@gmail.com'
        INSTRUCTOR = 'qasimalik@gmail.com'
    }

    stages {
        stage('Fetch latest data') {
            steps {
                checkout scm
                script {
                    env.GIT_SHA = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                }
                sh 'echo "Commit: $GIT_SHA"; wc -l dataset/train.csv'
            }
        }

        stage('Build image and train') {
            steps {
                // The Dockerfile installs dependencies and runs train.py on the latest dataset
                // Start from scratch: remove the old container and image, then rebuild without cache
                sh '''
                    docker rm -f $CONTAINER || true
                    docker rmi -f $IMAGE:latest || true
                    docker build --no-cache --build-arg GIT_COMMIT=$GIT_SHA -t $IMAGE:latest .
                '''
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm $IMAGE:latest python -m pytest -q'
            }
        }

        stage('Deploy on EC2') {
            steps {
                sh '''
                    docker rm -f $CONTAINER || true
                    docker run -d --name $CONTAINER --restart unless-stopped -p 8000:8000 $IMAGE:latest
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    for i in $(seq 1 30); do
                        if curl -sf http://localhost:8000/metrics > metrics_out.json; then
                            cat metrics_out.json; echo
                            grep -q "$GIT_SHA" metrics_out.json && exit 0
                        fi
                        sleep 3
                    done
                    docker logs --tail 50 $CONTAINER || true
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            script {
                def metrics = sh(returnStdout: true, script: 'curl -s http://localhost:8000/metrics || echo "metrics unavailable"').trim()
                emailext(
                    from: env.SENDER,
                    to: "${env.INSTRUCTOR},${env.SENDER}",
                    subject: "[${env.STUDENT_ID}] MIDTERM-${env.STUDENT_ID} build #${env.BUILD_NUMBER} - ${currentBuild.currentResult}",
                    body: "Student Reg No: ${env.STUDENT_ID}\nBuild result: ${currentBuild.currentResult}\nJob: ${env.JOB_NAME}\nBuild: #${env.BUILD_NUMBER}\nCommit: ${env.GIT_SHA}\nURL: ${env.BUILD_URL}\n\n/metrics:\n${metrics}\n"
                )
            }
            sh 'docker image prune -f || true'
        }
    }
}
