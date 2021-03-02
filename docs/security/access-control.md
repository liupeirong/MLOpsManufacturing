
# Azure Resources Access Control

You might want to grant different permissions to each persona. This document illustrates how to configure access control for Azure resources.

- [Azure Resources Access Control](#azure-resources-access-control)
  - [<a href="#anchor0">Access Control - Azure DevOps</a>](#access-control---azure-devops)
  - [Organization-level permissions](#organization-level-permissions)
    - [Current setting](#current-setting)
  - [Project-level permissions](#project-level-permissions)
    - [Current setting](#current-setting-1)
  - [How to restrict access to ADO for QA team?](#how-to-restrict-access-to-ado-for-qa-team)
  - [<a href="#anchor1">Access Control - Azure ML</a>](#access-control---azure-ml)
    - [Groups using Azure Active Directory](#groups-using-azure-active-directory)
  - [What QA team should NOT do?](#what-qa-team-should-not-do)
  - [What QA team should do?](#what-qa-team-should-do)
  - [How to restrict access to AML for QA team?](#how-to-restrict-access-to-aml-for-qa-team)
  - [How to create custom role to restrict specific actions?](#how-to-create-custom-role-to-restrict-specific-actions)
  - [<a href="#anchor2">Access Control - Azure Storage Account</a>](#access-control---azure-storage-account)
    - [Groups using Azure Active Directory](#groups-using-azure-active-directory-1)
    - [How to give QA team access to only test data folder?](#how-to-give-qa-team-access-to-only-test-data-folder)
  - [<a href="#anchor3">Access Control - Azure Dashboard</a>](#access-control---azure-dashboard)
    - [Groups using Azure Active Directory](#groups-using-azure-active-directory-2)
  - [How to give QA team access to only Dashboard?](#how-to-give-qa-team-access-to-only-dashboard)
  - [<a href="#anchor4">Access Control - Azure Key Vault</a>](#access-control---azure-key-vault)

<a id="anchor0"></a>

## <a href="#anchor0">Access Control - Azure DevOps</a>

## Organization-level permissions

- Only Dev members
- No QA members

### Current setting

Reference:

- [Collection-level groups](https://docs.microsoft.com/en-us/azure/devops/organizations/security/permissions?view=azure-devops&tabs=preview-page#collection-level-groups)
- [Organization-level permissions](https://docs.microsoft.com/en-us/azure/devops/organizations/security/permissions?view=azure-devops&tabs=preview-page#organization-level-permissions)

|Group name|Permissions|Membership|Who|
|-|-|-|-|
|Project Collection Administrators|Has permissions to perform all operations for the collection.|Contains the Local Administrators group (BUILTIN\Administrators) for the server where the application-tier services have been installed. Also, contains the members of the CollectionName\Service Accounts group.<br>This group should be restricted to the smallest possible number of users who need total administrative control over the collection. For Azure DevOps, assign to administrators who customize work tracking.|**Platform Admin**|
|Project Collection Valid Users|Has permissions to access team projects and view information in the collection.|Contains all users and groups that have been added anywhere within the collection. You cannot modify the membership of this group.|**Data Scientist**|

## Project-level permissions

- Dev members
- No QA members

### Current setting

Reference:

- [Project-level groups](https://docs.microsoft.com/en-us/azure/devops/organizations/security/permissions?view=azure-devops&tabs=preview-page#project-level-groups)
- [Project-level permissions](https://docs.microsoft.com/en-us/azure/devops/organizations/security/permissions?view=azure-devops&tabs=preview-page#project-level-permissions)

|Group name|Permissions|Membership|Who|
|-|-|-|-|
|Contributors|Has permissions to contribute fully to the project code base and work item tracking. The main permissions they don't have or those that manage or administer resources.|By default, the team group created when you create a project is added to this group, and any user you add to the team will be a member of this group. In addition, any team you create for a project will be added to this group by default, unless you choose a different group from the list.|**Data Scientist**|
|Project Administrators|Has permissions to administer all aspects of teams and project, although they can't create team projects.|Assign to users who manage user permissions, create or edit teams, modify team settings, define area an iteration path, or customize work item tracking.|**Platform Admin**|
|{team name}|Has permissions to contribute fully to the project code base and work item tracking. The default Team group is created when you create a project, and by default is added to the Contributors group for the project. Any new teams you create will also have a group created for them and added to the Contributors group.|Add members of the team to this group.|**Data Scientist**|

## How to restrict access to ADO for QA team?

Simply Platform Admin should not give organization-level and project-level ADO permissions to QA team members.

<a id="anchor1"></a>

## <a href="#anchor1">Access Control - Azure ML</a>

### Groups using Azure Active Directory

Create two groups using Azure Active Directory.
|Group Name|Attribute|
|-|-|
|{team name} for Dev members|Main Engineering group who needs to tune data and use Azure Machine Learning|
|{team name} for QA members|Q&A teams who should access only test data|

Each group has the following access:
|Resource Name|{team name} for Dev members|{team name} for QA members|
|-|-|-|
|Subscription|Contributor|**No Access**|
|Resource Group for dev|Contributor|**No Access**|
|Resource Group for stage|Contributor|**No Access**|
|[Function App "func-trigger-{BaseName}"](../../common/pipeline_trigger/README.md)|Contributor|**No Access**|
|Storage Account for dev|Contributor|**No Access**|
|Storage Account for stage|Contributor|**Reader**|

## What QA team should NOT do?

- Not see the details on Azure DevOps and Azure ML

## What QA team should do?

- Run a performance experiment pipeline
- Add/Delete test data to/from folders "test-pcm", "test-meta"
- See experiment results on Azure Dashboard
- Receive notifications when experiment is started and ended via email/Microsoft Teams/Slack.

## How to restrict access to AML for QA team?

- Access only specific folders for test data in storage
- Access Azure Dashboard to see performance experiment results
- Use managed service identity and Azure Function ([HTTP trigger](../../common/pipeline_trigger/README.md)) to run a performance experiment pipeline with key and test config file path

*QA team cannot access to even Azure Function resource.

*Azure Function can access to AML with managed service identity.

## How to create custom role to restrict specific actions?

Once you add an AAD group as contributor, people in the group can do almost anything for the resource.

Creating custom role is another option to achieve the requirement in order to reduce permissions for QA team as much as possible.

Please refer to [the document - Create custom role](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-assign-roles#create-custom-role) to know more details.

<a id="anchor2"></a>

## <a href="#anchor2">Access Control - Azure Storage Account</a>

### Groups using Azure Active Directory

Create four groups using Azure Active Directory.
|Group Name|Attribute|
|-|-|
|{team name} for Dev members|Main Engineering group who needs to tune data and use Azure Machine Learning|
|{team name} for QA members|Q&A teams who should access only test data|

Each group has the following access:
|Group Name|Data - Test Data|Data - all others|
|-|-|-|
|{team name} for Dev members|〇|〇|
|{team name} for QA members|〇|×|

### How to give QA team access to only test data folder?

Each setting for QA team is below:

|Resource|Role|
|-|-|
|Subscription|**No Access**|
|Storage Account for dev|**No Access**|
|Storage Account for stage|**Reader**|
|Container - shared (storage account for dev)|**read/execute**|
|Folders - Test Data (storage account for stage)|**read/write/execute**|

Note: The timing of setting above should be before creating other folders.

<a id="anchor3"></a>

## <a href="#anchor3">Access Control - Azure Dashboard</a>

### Groups using Azure Active Directory

Create four groups using Azure Active Directory.
|Group Name|Attribute|
|-|-|
|{team name} for Dev members|Main Engineering group who needs to tune data and use Azure Machine Learning|
|{team name} for QA members|Q&A teams who should access only test data|

Each group has the following access:
|Resource Name|{team name} for Dev members|{team name} for QA members|
|-|-|-|
|Subscription|Contributor|**No Access**|
|Resource Group|Contributor|**No Access**|
|Dashboard for Dev team|Contributor|**No Access**|
|Dashboard for QA team (experiment result)|Contributor|**Reader**|

## How to give QA team access to only Dashboard?

What QA team should do:

- See experiment results on Dashboard

QA team does not need to have access to subscription and resource groups, need to access only dashboard to see experiment results.

<a id="anchor4"></a>

## <a href="#anchor4">Access Control - Azure Key Vault</a>

You can check who can access to key vault on "Access Policies" pane.

- Azure DevOps account (Check Azure AD account)
- Managed Identity for Azure Functions (if secrets from key vault (e.g. connecting strings) were added as not key vault link but just secrets to Azure Functions app settings on CI, managed identity not needs to be added)
- Person who manages secrets on Key Vault (**Note: if person who is in access control list he/she can add himself/herself/anyone to Access Policy**)
