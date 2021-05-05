# Machine Learning Data Caching and Lineage

This document covers 2 crucial components of Machine Learning Data Operations:

1. Data Caching - for optimizing data access and reducing compute overhead.
1. Data Lineage - for providing observability and repeatability of pipeline runs and experiments with regards to the data they use.

## Data Caching in Azure Machine Learning

Running Machine Learning pipelines and experiments over large datasets on GPU requires paying attention to resource bottlenecks that may cause overhead on utilization and overall cost increase.

When using Azure Machine Learning with GPU compute cluster and data in Azure Storage, the connection between virtual machines and storage accounts may quickly become a factor that slows down training pipelines, effectively making expensive GPU nodes wait for the data to be delivered. This is why [we recommend using Premium Storage Accounts as primary datastores for running Azure Machine Learning pipelines](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-access-data#storage-guidance).

This strategy is particularly effective in training computer vision models because large amount of image data can be stored cost effectively in Azure Blob Storage, and archieved in cool tiers over time. Meanwhile, prior to running Azure Machine Learning pipelines, data can be copied to Premium storage for fast access by the training cluster.

### What to cache

When identifying files to be copied between storages for caching, we usually deal with one of two cases:

1. Whole dataset transfer from the long-term storage location to the cache location.
1. Partial transfer based on a list of files to copy.

Second case is a situation when an actual set of file to use is a significantly smaller part of the dataset. It's very typical for specific experiment pipelines or integration tests. While it may optimize premium storage utilization and caching time, maintaining lists of files to copy requires additional investment, such as annotations processing. For example, if annotations are stored in Pascal VOC format, there may be a code component that builds a list of labeled images so that only these files are cached.

### Recommended Data Caching Strategy

If images are mostly shared between pipelines and experiments in a single cache storage, caching the whole dataset is an optimal choice as it doesn't bring additional complication to data management.

## Data Lineage in Azure Machine Learning

**Model reproducibility** is a critical component of production-grade machine learning pipelines. Without it, Data scientists risk having limited visibility into what causes changes in model performance. The variability may appear to be caused by an adjustment of one parameter, but may actually be caused by hidden sources of randomness. Reproducibility reduces or eliminates variations when rerunning failed jobs or prior experiments, making it essential in the context of fault tolerance and iterative refinement of models. Running ML pipelines in the cloud across multiple compute nodes not only multiplies the sources of non-determinism but also increases the need for both fault tolerance and iterative model development.

There are 5 major components that define a machine learning model:

1. Model architecture
1. Model hyperparameters
1. Training code
1. Data augmentation code and parameters
1. Data and annotations

First 4 components are tracked between pipeline's Git repository and Azure Machine Learning tracking storages. Therefore, it's relatively easy to achieve model reproducibility up to the point of what data was used.

Data and annotations are much harder to track. There are tools and processes to maintain data versioning that can provide a great level of observability on data. However, with Azure Machine Learning pipelines, the same level of observability may be achieved with significantly lower effort. For example, here's what we can do when training computer vision models.

1. Maintain snapshots of annotation files as they are expected to change. Every pipeline run has a snapshot of annotation files in the run's output storage.
1. Maintain a single shared cache of data files (images) as they are expected to stay unmodified once added to the storage.
1. Model training code uses dataset annotation data to get references to data files (images). As data files are added over time, previous experiments are still fully reproducible based on the stored annotation snapshots.

### Recommended Data Lineage Strategy

For computer vision models trained on Azure Machine Learning pipelines, we recommend the following strategy:

1. Every pipeline run performs differential caching of the entire set of data files (images) in a Premium Blob Storage container (cache container).
1. Every pipeline run takes a snapshot of dataset annotations/labels, and stores it as the pipeline run's output. Such snapshot is attributed with a unique *snapshot name*.
1. Pipeline runs must support 2 modes: with the *latest data* or in the *reproduction mode*.
    1. When running on the *latest data*, a new snapshot of annotations/labels should be copied to the cache container, to a run-specific location defined by the *snapshot name*. The same files are uploaded to the run's output folder.
    1. When running in the *reproduction mode*, annotations/labels are downloaded from the output storage of the run that is being reproduced. The location of the snapshot in the cache container is defined by the *snapshot name* of the run that is being reproduced.

Different locations (prefixes) of the shared cache and annotation snapshots in a Premium Blob Storage container should be used for configuring different lifecycle management policies (TTL). Annotation snapshots don't need to be preserved as long as the shared cache.

## Data Caching Trade Study and Recommendations

Computer vision pipelines on Azure Machine Learning require transferring data from long-term storage in Azure Blob to a Premium Azure Blob container used as a cache. There are 4 major options of performing such data transfer in Azure ML pipelines:

1. PythonScriptStep with custom code on top of the Azure Storage SDK or [AzCopy](https://docs.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-copy).
1. Durable Azure Functions with custom code on top of the Azure Storage SDK or AzCopy.
1. [DataTransferStep](https://docs.microsoft.com/en-us/python/api/azureml-pipeline-steps/azureml.pipeline.steps.data_transfer_step.datatransferstep?view=azure-ml-py), a specialized step in Azure Machine Learning, utilizes Azure Data Factory (Copy Activity).
1. PythonScriptStep directly initiating an Azure Data Factory pipeline with [Copy Activity](https://docs.microsoft.com/en-us/azure/data-factory/copy-activity-overview).  

 Option | Pros | Cons |
| -------- | --- | ----------- |
| PythonScriptStep with AzCopy | Fast and efficient, provides required features | Storage credentials must be exposed to the step (directly, via Key Vault, or to AML compute's identity) |<!-- markdownlint-disable MD013 -->
| Durable Functions | Fast and efficient, provides almost all required features, no need to expose storage credentials to pipelines | Significantly increases run orchestration complexity, adds manageability overhead, no access to AML run output |<!-- markdownlint-disable MD013 -->
| DataTransferStep | Lowest manageability overhead, storage credentials are managed within AML Datastores | Doesn't support incremental copying |
| Azure Data Factory | no need to expose storage credentials to pipelines | Same as above + manageability overhead |<!-- markdownlint-disable MD013 -->

Option "PythonScriptStep with AzCopy" is a clear winner by the following reasons:

1. It has greater flexibility and AzCopy provides a highly efficient data transfer mechanism with maximum performance.
1. It runs within AML pipelines, and has access to all pipeline's and run's subsystems.
1. Storage credentials exposure can be mitigated (see below).

### Managing Storage Credentials in AML Pipelines

When a certain code component running within an AML pipeline requires direct access to Azure Storage, there are multiple ways to provide it:

1. Pass Account Key or SAS-token as AML Pipeline Parameters (**not recommended**).
1. Store storage access credentials in [AML workspace's Key Vault](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-secrets-in-runs)
1. Isolate code that requires direct storage access to a separate PythonScriptStep (ParallelRunStep) running on an AML compute cluster with a [managed identity](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview). Such identity must be given appropriate access to the storage resources. This option should be used once Managed Identity support in azure ML reaches General Availability status.

## Data Caching and Data Lineage Implementation

Data caching and lineage can be implemented for computer vision as a PythonScriptStep running within the following steps.

### Pre-req: Configure the following arguments of a pipeline run

* `dataset_prefix_name` - a dataset-specific name that will uniquely identify a dataset specific-location in the cache container.
* `source_datastore_name` - source data store, an Azure ML Datastore (Blob, ADLS Gen2 or File Shares) where the dataset is stored long-term.
* `source_datastore_data_path` - a directory/prefix in the the source data store where the data files (images) are stored.
* `source_datastore_annotations_path` - a directory/prefix in the the source data store where annotation files are stored.
* `cache_datastore_name` - cache data store, an Azure ML Datastore configured on a premium storage container in Blob, ADLS Gen2 or File Shares.
* `cache_data_dir_name` - name of the last component of the data cache path (e.g. `data`).
* `cache_annotations_dir_name` - name of last component of the annotation snapshot cache path (e.g. `annotations`).

Additional variables are expected to be assigned within the pipeline configuration process:

* `snapshot_name` - a unique name generated for a run. If reproducing another run, this name should be taken from tags of the run that is being reproduced
* `source_datastore_url` - URL of the source datastore container.
* `source_datastore_secret_name` - name of the workspace KeyVault secret where the source datastore account key or SAS token is stored.
* `cache_datastore_url` - URL of the cache datastore container.
* `cache_datastore_secret_name` - name of the workspace KeyVault secret where the cache datastore account key or SAS token is stored.
* `cache_datastore_data_path` - built as `{source_datastore_name}/{dataset_prefix_name}/{cache_data_dir_name}`
* `cache_datastore_annotations_path` - built as `{source_datastore_name}/{dataset_prefix_name}/{cache_annotations_dir_name}/{snapshot_name}`

### Step 1 - Populate the annotation snapshot cache

Annotation snapshot is always downloaded to a temporary directory `annotations_local_dir`.

If it's a run that is *reproducing another run*, then a snapshot of annotations is downloaded to `annotations_local_dir` from the output folder of the run that is being reproduced (using Azure ML `Run.download_files` function). it is then copied to the snapshot location in the cache datastore.

```bash
azcopy cp "{annotations_local_dir}/*" "{cache_datastore_url}/{cache_datastore_annotations_path}"
```

If this is a *new* run, the annotation snapshot is made by directly copying from the source datastore. At the same time, annotations are also downloaded to `annotations_local_dir` so they can be uploaded to the run's output later.

```bash
azcopy cp "{source_datastore_url}/{source_datastore_annotations_path}/*" "{cache_datastore_url}/{cache_datastore_annotations_path}"
azcopy cp "{cache_datastore_url}/{cache_datastore_annotations_path}/*" "{annotations_local_dir}" 
```

### Step 2 - Populate and update data cache

`overwrite` option of AzCopy is set to `ifSourceNewer` which make the process a lot faster if files in the cache are not older than ones in the source datastore.

```bash
azcopy cp "{source_datastore_url}/{source_datastore_data_path}/*" "{cache_datastore_url}/{cache_datastore_data_path}"
```

### Step 3 - Upload annotation snapshot to the run's output

Azure ML `Run.upload_folder` function is used for uploading the annotation snapshot to the current run's output folder constructed as `{DATAPREP_PREFIX}.{dataset_prefix_name}.{_ANNOTATIONS_COPY_NAME}`, where

* DATAPREP_PREFIX is `mldl.dataprep`
* _ANNOTATIONS_COPY_NAME is `annotations`

### Final cache structure

The following final cache structure will be provisioned in the Premium storage cache container.

```text
[{source_datastore_name}]
└── [{dataset_prefix_name}]
    └── [{cache_data_dir_name}]
    └── [{cache_annotations_dir_name}]
        └── [{snapshot_name}]
```

As an example, let's use the following values:

* **source_datastore_name** is `longterm-datastore`
* **dataset_prefix_name** is `coco` (can assign any name here)
* **cache_data_dir_name** is `data`
* **cache_annotations_dir_name** is `annotations`
* **snapshot_name** is `9D299F782E35485F9A4B86A8EA0A93B7` (a generate random value)

The cache structure would be the following:

```text
[longterm-datastore]
└── [coco]
    └── [data]
    └── [annotations]
        └── [9D299F782E35485F9A4B86A8EA0A93B7]
```

### Using cached data in the training steps

Based on the cache structure, data and annotations must be passed to training steps as 2 separate Azure ML File Datasets in the `mount` mode:

1. File dataset made on `{source_datastore_name}/{dataset_prefix_name}/{cache_data_dir_name}`
1. File dataset made on `{source_datastore_name}/{dataset_prefix_name}/{cache_annotations_dir_name}/{snapshot_name}`

Using the same example, it would be:

1. File dataset made on `longterm-datastore/coco/data`
1. File dataset made on `longterm-datastore/coco/annotations/9D299F782E35485F9A4B86A8EA0A93B7`

When passed to a training step as `as_mount()` results, they will be resolved to 2 parameters containing filesystem paths where the corresponding cache storage located are mounted by Azure ML compute engine.

## Data (Images) and Annotations directory structure

In machine learning Pipelines, the same data files (images) are used across multiple datasets and ML models. At the same time, we may have multiple different data collection and labeling processes that include pre-processing, merging, and structuring the storage for different purposes. In order to make the process flexible and efficient, we propose the following structure of the long term dataset storage.

### Data (Images)

Images are stored within a structure that reflects the data collection process. For example, if images are collected from pre-defined locations and known data collection devices (cameras), the following structure can be leveraged:

```text
[images]
└── [{location_name}]
    └── [{camera_id}]
        └── [{year}]
            └── [{month}]
                ├── image1.jpg
                ├── image2.jpg
                └── ...
```

This approach makes image collection independent of the labeling process.

### Annotations

Due to the modern practices on annotation/labeling for computer vision data, the process of labeling on datasets that change over time includes 2 traits:

1. Labeled images are referenced as they are stored in data storage.
1. There is always a "merging" labels step for grouping images into a single labeling set. It either happens as part of the labeling itself, or during the data preparation steps.

Our practice shows that regardless of the labeling type (images tags for classification, object identification with bounding boxes, instance segmentation, etc.), what makes labels across multiple sets being grouped and used together is a notion of **dataset**. A single image may be used across many datasets, but a single label will be most likely used only within a single dataset. Even when a label is leveraged across multiple datasets, most likely, it will be augmented with dataset-specific attributes, and therefore better be copied to a dataset-specific location. Dataset is what defines a group of *labeled* images/files.

Labels define the dataset structure and purposes of different image groups such as training, fine-tuning, testing, and validation. To manage across all labels, we propose to store them by groups as following. The training code should be able to process the labels folder structure.

1. Labels are stored under a dataset name.
1. Every label file is named as `{location_name}.{camera_id}.{unique_file_id}`. unique_file_id must be a unique value withing a group of files with the same location_name and camera_id.
1. *When possible*, label files are placed according to their primary purpose within the training process (e.g. `train`, `test`).

> If a random runtime shuffling/splitting is used, for a purpose of experiment reproducibility the split information (file list for every group) must be stored in the run's output storage, and reproduced in derived runs.

Here are a few examples with dataset name `object_detection` and labels in `.csv` format.

**Example 1** - annotations are stored by the data category

```text
[object_detection]
└── [train]
    ├── {location_name}.{camera_id}.029347623462.csv
    ├── {location_name}.{camera_id}.029347346341.csv
    └── {location_name}.{camera_id}.235235994566.csv
└── [test]
    ├── {location_name}.{camera_id}.029347623410.csv
    ├── {location_name}.{camera_id}.029347346395.csv
    └── {location_name}.{camera_id}.235232302300.csv    
└── [validation]
    ├── {location_name}.{camera_id}.029347678464.csv
    ├── {location_name}.{camera_id}.462747346320.csv
    └── {location_name}.{camera_id}.556435994562.csv      
```

**Example 2** - annotations are stored by the model stage category

```text
[object_detection]
└── [train] <- for runtime train/test/val split
    ├── {location_name}.{camera_id}.029347623462.csv
    ├── {location_name}.{camera_id}.029347346341.csv
    └── {location_name}.{camera_id}.235235994566.csv
└── [qa_validation] <- for QA validation tests
    ├── {location_name}.{camera_id}.029347623410.csv
    ├── {location_name}.{camera_id}.029347346395.csv
    └── {location_name}.{camera_id}.235232302300.csv      
```

**Example 3** - annotations are stored by the model stage category and time

> **This is the recommended label storage structure**

```text
[object_detection]
└── [train] <- for runtime train/test/val split
│   └── [{year}.{month}]
│   │   ├── {location_name}.{camera_id}.029347623462.csv
│   │   ├── {location_name}.{camera_id}.029347346341.csv
│   │   └── {location_name}.{camera_id}.235235994566.csv
└── [qa_validation] <- for QA validation tests
    ├── {location_name}.{camera_id}.029347623410.csv
    ├── {location_name}.{camera_id}.029347346395.csv
    └── {location_name}.{camera_id}.235232302300.csv      
```

There are labels that are yet to be verified, such as those made using transfer learning or another auto-labeling technique. For these labels, the storage structure needs to reflect the state in the data collection and verification processes. On the data collection side, the source (location, camera id) should be presented in the structure. On the verification side, the state of the labels should be presented: auto-labeled as 'positive', auto-labeled as 'negative', and 'verified'. All verified labels must be further processed/converted and transferred to the `train` (default) or `qa_validation` subsets.

```text
[object_detection] <- dataset name
└── [unverified]
│   ├── [positive]
│   │    └── [{location_name}]
│   │        └── [{camera_id}]
│   │            ├── {location_name}.{camera_id}.029347623462.csv
│   │            ├── {location_name}.{camera_id}.029347346341.csv
│   │            └── {location_name}.{camera_id}.235235994566.csv
│   └── [negative] <- same as in positive
└── [verified]
    └──[{year}.{month}]
       ├── {location_name}.{camera_id}.029347623410.csv
       ├── {location_name}.{camera_id}.029347346395.csv
       └── {location_name}.{camera_id}.235232302300.csv      
```
