# Data Preprocessing

This folder contains samples and templates for data preprocessing steps with
Azure Machine Learning Pipelines.

## Explaining data preprocessing with non-python tooling for AML

The [wrapper script](./preprocess_os_cmd_aml.py) calls the command line command.
In the basic sample it is just a `cp` to move data from
the input folder to the output folder of it's AML pipeline step.

```python
    process = subprocess.Popen(['cp',
                                '{0}/.'.format(mount_context.mount_point),
                                step_output_path, '-r', '-v'],
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
```

So it is possible to call any tool or program which can be executed on a ubuntu
linux (which is the base image for AML pipeline steps).
The tool(s) need to be installed in the [custom container image](./Dockerfile).

Important to know is that the input folder is getting mounted within the wrapper script here, so you can only work on
the data after this code:

```python
    mount_context = dataset.mount()
    mount_context.start()
    print(f"mount_point is: {mount_context.mount_point}")
```

The mount point or folder is stored in this attribute
`mount_context.mount_point` and can be used in the command line call.
As well as the output folder path for this step which is stored in `step_output_path`.

## Example: Setup image preprocessing with ImageMagick

As an example on how to extend this template I will use this [blog post](https://vitux.com/how-to-resize-images-on-the-ubuntu-command-line/)
about resizing images with [ImageMagick](https://imagemagick.org/index.php).

1. Adding ImageMagick to the **Dockerfile** for the custom preprocessing step
2. Change the command line call in the **Wrapper script**
3. Rebuilding, publish and run the **data_processing_os_cmd_pipeline**

### Adding ImageMagick to the Dockerfile for the custom preprocessing step

Adding the installation instruction `apt-get install -y imagemagick && \` to the [Dockerfile](./Dockerfile)
just before `apt-get clean` is called:

```dockerfile
RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 && \
    apt-get install -y fuse && \
    apt-get install -y imagemagick && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*
```

### Change the command line call in the Wrapper script

>Assumption: Input pictures are all jpg and output pictures should be 100x100.
Input dataset is <http://download.tensorflow.org/example_images/flower_photos.tgz>,
only convert the subfolder daisy will be resized.

Changing the command to:

```python
    process = subprocess.Popen(['convert',
                                '{0}/daisy/*.jpg'.format(mount_context.mount_point),
                                '-resize',
                                '100x100!',
                                '{0}/resized.jpg'.format(step_output_path)],
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
```

### Rebuilding, publish and run the data_processing_os_cmd_pipeline

For local dev test the variable `AML_REBUILD_ENVIRONMENT` in `.env` file needs to be set to true.

```bash
# Flag to allow rebuilding the AML Environment after it was built for the first time. This enables dependency updates from conda_dependencies.yaml.
AML_REBUILD_ENVIRONMENT = 'true'
```

If the local dev test is set up correct you can publish and execute the
pipeline with following commands from project root folder:

```bash
python -m ml_service.pipelines.build_data_processing_os_cmd_pipeline
```

```bash
python -m ml_service.pipelines.run_data_processing_pipeline --aml_pipeline_name "flower-custom-preprocessing-pipeline"
```

For stage and production you have to check in the code and run through
review and AzDO pipeline process.
