<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories" minScale="1e+08" version="3.18.3-Zürich" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal enabled="0" mode="0" fetchMode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <property key="WMSBackgroundLayer" value="false"/>
    <property key="WMSPublishDataSourceUrl" value="false"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="identify/format" value="Value"/>
  </customproperties>
  <pipe>
    <provider>
      <resampling enabled="false" zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer nodataColor="" classificationMax="7080825856" classificationMin="0" alphaBand="-1" type="singlebandpseudocolor" opacity="1" band="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader minimumValue="0" maximumValue="7080825856" classificationMode="2" clip="0" colorRampType="INTERPOLATED" labelPrecision="4">
          <colorramp type="gradient" name="[source]">
            <Option type="Map">
              <Option type="QString" name="color1" value="0,68,27,255"/>
              <Option type="QString" name="color2" value="247,252,245,255"/>
              <Option type="QString" name="discrete" value="0"/>
              <Option type="QString" name="rampType" value="gradient"/>
              <Option type="QString" name="stops" value="0.1;0,109,44,255:0.22;35,139,69,255:0.35;65,171,93,255:0.48;116,196,118,255:0.61;161,217,155,255:0.74;199,233,192,255:0.87;229,245,224,255"/>
            </Option>
            <prop k="color1" v="0,68,27,255"/>
            <prop k="color2" v="247,252,245,255"/>
            <prop k="discrete" v="0"/>
            <prop k="rampType" v="gradient"/>
            <prop k="stops" v="0.1;0,109,44,255:0.22;35,139,69,255:0.35;65,171,93,255:0.48;116,196,118,255:0.61;161,217,155,255:0.74;199,233,192,255:0.87;229,245,224,255"/>
          </colorramp>
          <item alpha="255" color="#00441b" label="0.0000" value="0"/>
          <item alpha="255" color="#2a924a" label="1770206464.0000" value="1770206464"/>
          <item alpha="255" color="#7bc87c" label="3540412928.0000" value="3540412928"/>
          <item alpha="255" color="#caeac3" label="5310619392.0000" value="5310619392"/>
          <item alpha="255" color="#f7fcf5" label="7080825856.0000" value="7080825856"/>
          <rampLegendSettings suffix="" minimumLabel="" useContinuousLegend="1" orientation="2" maximumLabel="" prefix="" direction="0">
            <numericFormat id="basic">
              <Option type="Map">
                <Option type="QChar" name="decimal_separator" value=""/>
                <Option type="int" name="decimals" value="6"/>
                <Option type="int" name="rounding_type" value="0"/>
                <Option type="bool" name="show_plus" value="false"/>
                <Option type="bool" name="show_thousand_separator" value="true"/>
                <Option type="bool" name="show_trailing_zeros" value="false"/>
                <Option type="QChar" name="thousand_separator" value=""/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast contrast="0" brightness="0" gamma="1"/>
    <huesaturation colorizeStrength="100" colorizeOn="0" colorizeRed="255" grayscaleMode="0" colorizeGreen="128" colorizeBlue="128" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
