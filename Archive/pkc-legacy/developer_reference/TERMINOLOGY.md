# Terminology

This file defines terms used throughout the Developer Reference.

## Surface

A developer-facing interface through which external code interacts with Premiere Pro. Examples: ExtendScript, UXP, CEP, QE DOM, C++ SDK.

## Contract

The documented behaviour of an object, method, property, file format, or runtime boundary, including side effects and failure modes.

## Official

Confirmed by Adobe documentation, SDK headers, or official Adobe repositories.

## Reverse Engineered

Derived from inspection or experimentation and not guaranteed by Adobe.

## ProjectItem

A project-panel item. It may represent media, bins, sequences, or other project entities depending on context.

## TrackItem

A timeline instance placed on a sequence track. A TrackItem is not the same as a ProjectItem.

## Media

An external source file or media resource referenced by project objects. Media is not owned by a Sequence.

## QE DOM

An undocumented or semi-documented internal scripting interface exposed through `qe` after QE is enabled. Treat as unstable unless verified.

## CEP

Common Extensibility Platform: HTML/JavaScript panel runtime with a bridge to ExtendScript.

## UXP

Unified Extensibility Platform: Adobe's modern plugin runtime used by current and future Premiere Pro extensibility APIs.
