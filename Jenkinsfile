pipeline {
    agent {
        docker { image 'anchit2698/testcontainer' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'docker run anchit2698/testcontainer'
            }
        }
    }
}
