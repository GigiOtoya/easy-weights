# Easy Weights Blender Add-on

## Overview

The Easy Weights Blender Add-on provides a user-friendly interface to transfer and clean vertex weights between mesh objects in Blender. This tool is designed to facilitate the workflow of artists and animators by allowing them to quickly transfer weights from a source mesh to one or multiple target meshes, and to clean up unnecessary vertex groups.

## Features

- Weight Transfer: Transfer vertex group weights from a source mesh to a target mesh or multiple meshes within a collection.
- Clean Vertex Groups: Remove vertex groups with zero weights from target meshes.
- Smooth Weights: Option to smooth weights for vertex groups during the transfer process.

## Installation

1. Download the Script: Save the provided Python script to your local machine.

2. Install the Add-on:

- Open Blender.
- Go to Edit > Preferences.
- Select the Add-ons tab.
- Click Install and navigate to the downloaded Python script.
- Enable the add-on by checking the box next to Easy Weights.

## Usage

### Easy Weights Panel

1. Access the Panel:

   - Open the 3D Viewport.
   - Navigate to the Easy Weights tab on the right sidebar.

2. Settings Section:

   - Source: Select the source mesh from which weights will be transferred.
   - Selection Mode: Choose between Single Mesh or Collection to determine if weights will be transferred to one target mesh or all meshes in a collection.
   - Target(s): Depending on the selection mode, choose the target mesh or the collection of meshes.
   - Clean: Enable this option to remove vertex groups with zero weights from the target mesh.
   - Smooth: Enable this option to smooth the weights for vertex groups.

3. Actions Section:

   - Transfer Weights: Click to transfer weights from the source to the selected target(s).
   - Clean Vertex Groups: Click to clean vertex groups with zero weights from the selected target(s).

## Detailed Class and Method Descriptions

### EasyWeightsProperty

A property group containing properties for source mesh, target mesh, target collection, selection mode, clean option, and smooth option.

### TransferWeightOperator

An operator to transfer weights from the source mesh to the target mesh(es).

- transferWeights: Transfers weights from the source to the target.
  execute: Executes the weight transfer process.

### CleanUpOperator

An operator to clean up vertex groups with zero weights from the target mesh(es).

- deleteZeroWeights: Deletes vertex groups with zero weights from the target.
- execute: Executes the cleanup process.

### EasyWeightPanel

A panel class to create the UI for the add-on in the 3D Viewport.

### Utility Functions

- getMeshObjects: Returns a list of mesh objects from a given list or collection.
- updatePanel: Forces the UI to update.

### Registration Functions

#### register

Registers all classes and adds the EasyWeightsProperty to the scene properties. Also appends updatePanel to the depsgraph update handlers.

#### unregister

Unregisters all classes and removes the EasyWeightsProperty from the scene properties. Also removes updatePanel from the depsgraph update handlers.
