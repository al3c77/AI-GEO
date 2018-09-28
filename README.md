# AI-GEO
OptOSS AI GEO Open Source code

## Scope of the project
Most of satellite data collected today is not studied by humans simply because the Earth is massive while the number of analysts is limited. AI will assist emergency authorities to detect effects of natural disasters by automating the processing of satellite imagery through the use of an Artificial Intelligence. This will help emergency fighters to detect even small changes to water bodies and surface displacements near inhabited areas and range them according to the impact on populations.

AI solution will primarily use Sentinel 1 interferometric Synthetic Aperture Radar (SAR) antenna imagery data, which are suitable for precise detection of floods and land surface changes.

### Components

#### client
KeplerGL based visualiser for Cloud Optimised GeoTIF images is a modern and convenient visualiser.

#### server
Web based tile server.

#### AI
Python 3.7 intelligent data pre-processor and clusterer that runs in Docker containers. Can be deployed to Kubernetes platform or execulted locally. This solution should work with unstructured satellite imagery and provide quick turnaround for rapid and precice change detection.

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg?longCache=true&style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
