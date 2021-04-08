#!/usr/bin/env python3
# -*- encoding: utf8 -*-
import os.path
import sys
import docopt
from qgis import processing
from qgis.core import *
# from qgis.core import (
#         QgsApplication,
#         # QgsPathResolver,
#         QgsProject,
#         QgsRasterLayer,
#         QgsReferencedRectangle,
#     )
from qgis.gui import (
        # QgisInterface,
        # QgsMapCanvas,
        QgsLayerTreeMapCanvasBridge,
    )
from PyQt5.QtGui import *


usage = """\
Create a QGis project for visualizing the output of the
lue_describe_flow_direction command

Usage:
    {command} <workspace>

Options:
    workspace    Directory containing the outputs to visualize
    -h --help    Show this screen
""".format(
    command = os.path.basename(sys.argv[0]))


black = QColor(0, 0, 0)
red = QColor(255, 0, 0)

# nord: Polar Night: four dark colors
nord0 = QColor(46, 52, 64)  # Dark
nord1 = QColor(59, 66, 82)  # Lighter than nord0
nord2 = QColor(67, 76, 94)  # Lighter than nord1
nord3 = QColor(76, 86, 106)  # Lighter than nord2

# nord: Snow Storm: three bright colors
nord4 = QColor(216, 222, 233)  # Bright
nord5 = QColor(229, 233, 240)  # Ligher than nord4
nord6 = QColor(236, 239, 244)  # Ligher than nord5

# nord: Frost: four bluish colors
nord7 = QColor(143, 188, 187)  # Calm, frozen polar water
nord8 = QColor(136, 192, 208)  # Bright, shiny, pure and clear ice
nord9 = QColor(129, 161, 193)  # Darkened, arctic waters
nord10 = QColor(94, 129, 172)  # Dark, deep arctic ocean

# nord: Aurora: Five colorful components
nord11 = QColor(191, 97, 106)  # Redish
nord12 = QColor(208, 135, 112)  # Orange
nord13 = QColor(235, 203, 139)  # Dark yellow
nord14 = QColor(163, 190, 140)  # Green
nord15 = QColor(180, 142, 173)  # Purple


def load_layer(
        workspace,
        project,
        basename,
        label):

    raster_pathname = "{}.tif".format(os.path.join(workspace, basename))
    raster_layer = QgsRasterLayer(raster_pathname, label)
    assert raster_layer.isValid()
    project.addMapLayer(raster_layer)

    return raster_layer


def visualize_elevation(
        raster_layer):

    data_provider = raster_layer.dataProvider()
    statistics = data_provider.bandStatistics(1, QgsRasterBandStats.All)
    shader_function = QgsColorRampShader(type=QgsColorRampShader.Interpolated)
    colours = [
            QgsColorRampShader.ColorRampItem(statistics.minimumValue, nord14,
                "{}".format(statistics.minimumValue)),
            QgsColorRampShader.ColorRampItem(statistics.maximumValue, nord11,
                "{}".format(statistics.maximumValue)),
        ]
    shader_function.setColorRampItemList(colours)
    raster_shader = QgsRasterShader()
    raster_shader.setRasterShaderFunction(shader_function)
    renderer = QgsSingleBandPseudoColorRenderer(raster_layer.dataProvider(), 1, raster_shader)
    raster_layer.setRenderer(renderer)


def visualize_flow_direction(
        raster_layer):
    # TODO
    # - visualize flow directions with nice colours (arrows?)
    pass


def visualize_inflow_count(
        raster_layer):

    # Wicked. This should be easier...
    colour_ramp = QgsStyle().defaultStyle().colorRamp("Plasma")
    offset = len(colour_ramp.stops()) / 8

    colours = [
            QgsColorRampShader.ColorRampItem(0, black, "0"),
            QgsColorRampShader.ColorRampItem(1, colour_ramp.stops()[round(0 * offset)].color, "1"),
            QgsColorRampShader.ColorRampItem(2, colour_ramp.stops()[round(1 * offset)].color, "2"),
            QgsColorRampShader.ColorRampItem(3, colour_ramp.stops()[round(2 * offset)].color, "3"),
            QgsColorRampShader.ColorRampItem(4, colour_ramp.stops()[round(3 * offset)].color, "4"),
            QgsColorRampShader.ColorRampItem(5, colour_ramp.stops()[round(4 * offset)].color, "5"),
            QgsColorRampShader.ColorRampItem(6, colour_ramp.stops()[round(5 * offset)].color, "6"),
            QgsColorRampShader.ColorRampItem(7, colour_ramp.stops()[round(6 * offset)].color, "7"),
            QgsColorRampShader.ColorRampItem(8, colour_ramp.stops()[round(7 * offset)].color, "8"),
        ]
    renderer = QgsPalettedRasterRenderer(
        raster_layer.dataProvider(), 1, classes=QgsPalettedRasterRenderer.colorTableToClassData(colours))
    raster_layer.setRenderer(renderer)


def visualize_inter_partition_stream(
        raster_layer):

    colours = [
            # QgsColorRampShader.ColorRampItem(0, nord10, "intra-partition stream"),
            QgsColorRampShader.ColorRampItem(1, red, "inter-partition stream"),
        ]
    renderer = QgsPalettedRasterRenderer(
        raster_layer.dataProvider(), 1, classes=QgsPalettedRasterRenderer.colorTableToClassData(colours))
    raster_layer.setRenderer(renderer)


if __name__ == "__main__":
    arguments = docopt.docopt(usage)

    workspace = arguments["<workspace>"]
    project_basename = os.path.basename(workspace)
    project_pathname = "{}.qgs".format(os.path.join(workspace, project_basename))

    QgsApplication.setPrefixPath("/usr", True)
    application = QgsApplication([], True)
    application.initQgis()

    # Create project
    project = QgsProject.instance()

    # Load layers and configure renderers
    raster_layer = load_layer(workspace, project, "elevation", "elevation")
    visualize_elevation(raster_layer)

    raster_layer = load_layer(workspace, project, "flow_direction", "flow direction")
    visualize_flow_direction(raster_layer)
    project.layerTreeRoot().findLayer(raster_layer.id()).setItemVisibilityChecked(False)

    raster_layer = load_layer(workspace, project, "inflow_count", "inflow count")
    visualize_inflow_count(raster_layer)
    project.layerTreeRoot().findLayer(raster_layer.id()).setItemVisibilityChecked(False)

    raster_layer = load_layer(workspace, project, "inter_partition_stream", "inter-/intra-partition stream")
    visualize_inter_partition_stream(raster_layer)

    view_settings = project.viewSettings()
    view_settings.setDefaultViewExtent(QgsReferencedRectangle(raster_layer.extent(), raster_layer.crs()))

    # Save project
    project_written = project.write(project_pathname)
    assert project_written

    application.exitQgis()

    print(project_pathname)



### # Manually define the colour ramp - alternatively load from an XML (untested)
### colour_list = [
###     QColor(5, 113, 176),
###     QColor(247, 247, 247),
###     QColor(202, 0, 32),
### ]
### colour_ramp_gradient.setColor1(QColor(5,113,176))
### colour_ramp_gradient.setColor2(QColor(202,0,32))
### colour_ramp_gradient.setStops(
###    [QgsGradientStop(0.25, QColor(146,197,222)),
###    QgsGradientStop(0.5, QColor(247,247,247)),
###    QgsGradientStop(0.75, QColor(244,165,130))]
### )
### 
### ramp_min = -20
### ramp_max = 20
### ramp_num_steps = 16
### 
### # Apply colour ramp for vector / points layer
### if input_layer.type() == QgsMapLayer.VectorLayer:
###     intervals = QgsClassificationEqualInterval().classes(
###         ramp_min, ramp_max, ramp_num_steps)
###     render_range_list = [QgsRendererRange(
###         i, QgsSymbol.defaultSymbol(input_layer.geometryType()))
###         for i in intervals]
###     renderer = QgsGraduatedSymbolRenderer(
###         values_field_name, render_range_list)
###     renderer.updateColorRamp(colour_ramp_gradient)
###     input_layer.setRenderer(renderer)
### 
### # Apply colour ramp for raster layer
### elif input_layer.type() == QgsMapLayer.RasterLayer:
###     num_intervals = len(colour_list)
###     c_bounds = numpy.linspace(
###         ramp_min, ramp_max, num_intervals).tolist()
###     shader_interval_list = [QgsColorRampShader.ColorRampItem(
###         c_bounds[i], colour_list[i], f'{c_bounds[i]}')
###         for i in range(num_intervals)]
###     cramp = QgsColorRampShader()
###     cramp.setColorRampType(QgsColorRampShader.Interpolated)
###     cramp.setColorRampItemList(shader_interval_list)
###     shader = QgsRasterShader()
###     shader.setRasterShaderFunction(cramp)
###     input_layer.dataProvider().setNoDataValue(1, 0)
###     renderer = QgsSingleBandPseudoColorRenderer(input_layer.dataProvider(), 1, shader)
###     renderer.setOpacity(0.6)
###     input_layer.setRenderer(renderer)
