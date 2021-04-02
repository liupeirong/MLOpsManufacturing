# LVA Topology Design <!-- omit in toc -->

This document outlines the topology design for the Live Video Analytics edge module. This sample project focuses on event-based recording
of assets. For more details on this scenario, you can read more in our [business logic document](/docs/design-business-logic.md).

This diagram represents the contents of the topology file we will be deploying.

**Event-Based Capture of Assets**:

1. Video is captured through an RTSP source
1. The gRPC extension will extract frames from the incoming video and send them to the AI inferencing Edge module and capture the results
1. The results will then be sent to the business logic module using the IoT Edge Hub
1. The business logic module will evaluate the AI results and if all conditions are met, it will send a message (`evrIoTMessageSource`)
   to LVA
1. The signal gate will need the RTSP source and `evrIoTMessageSource` to open
1. When the signal gate conditions are met, the asset sink will save the video to Azure Media Services

![LVA Topology](/docs/images/lva-topology.png)
