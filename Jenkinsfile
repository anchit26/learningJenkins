pipeline {
    agent {
        docker { image 'anchit2698/learningdocker' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'docker images'
            }
        }
    }
}
