@Library('slack-notification')
import org.gradiant.jenkins.slack.SlackNotifier

pipeline {
    agent none

    stages {
        stage('Tests') {
            parallel {
                stage('shell') {
                    agent { label 'script' }
                    steps {
                        sh script: 'typos', label: 'check typos'
                        sh script: './qa-test --shell', label: 'shell scripts lint'
                    }
                    post {
                        always {
                            // linters results
                            recordIssues enabledForFailure: true, failOnError: true, sourceCodeEncoding: 'UTF-8',
                                         tool: checkStyle(pattern: '.shellcheck/*.log', reportEncoding: 'UTF-8', name: 'Shell scripts')
                        }
                        fixed {    
                            script {
                                new SlackNotifier().notifyResult("shell-team")
                            }
                        }
                        failure {   
                            script {
                                new SlackNotifier().notifyResult("shell-team")
                            }
                        }
                    }
                }
            }
        }
    }
}
