# Alfred AWS SSM Connect
Alfred workflow and universal action to connect to AWS instances using Systems Manager Session Manager.

! This is a bit hacky and needs improvement !


![SSM](docs/ssm.png?raw=true "ssm")

## Requirements

- jq (https://stedolan.github.io/jq/) 
  - `brew install jq`

- AWS CLI (https://aws.amazon.com/cli/)
  - `brew install aws`

- AWS Credentials in `~/.aws/credentials`

- Python 3.7

- AWS instances setup with SSM session manager (https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)

## Usage

- Download and Run `aws-ssm-connect.alfredworkflow`

### Workflow

- Open Alfred and type `ssm`
- Select the credential you wish to use
- Select the instance to connect to
  - ⏎ use ssm session manager to connect to the instance
  - ⌘ + ⏎ to copy the instance id


### Universal Action

- Select a instance id
- Open universal actions 
- Select the credential you wish to use

![Universal Action](docs/universal.png?raw=true "universal")


