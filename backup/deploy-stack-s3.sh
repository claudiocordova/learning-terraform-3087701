aws cloudformation deploy --stack-name kronos-s3-staging --template-file ./s3.yaml --capabilities CAPABILITY_NAMED_IAM  --parameter-overrides ParameterKey=EnvironmentParameter,ParameterValue=staging
