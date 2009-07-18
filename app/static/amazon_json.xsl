<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:aws="http://webservices.amazon.com/AWSECommerceService/2005-10-05" exclude-result-prefixes="aws">

	<xsl:output method="text"/>

<!-- +- -->
<!-- | Base Template Match, General JSON Format -->
<!-- +- -->
	<xsl:template match="/">
		<xsl:value-of select="aws:ItemLookupResponse/aws:OperationRequest/aws:Arguments/aws:Argument[@Name = 'CallBack']/@Value" /><xsl:text> { "Item" : </xsl:text><xsl:apply-templates/><xsl:text> } </xsl:text>
	</xsl:template>
	
	<xsl:template match="aws:RequestId"></xsl:template>
	<xsl:template match="aws:RequestProcessingTime"></xsl:template>
	<xsl:template match="aws:Items">
		<xsl:apply-templates select="aws:Item"/>
	</xsl:template>
	
<!-- +- -->
<!-- | Fetch ASIN, URL, Title, Price, Description and return as oembed.com photo type json object -->
<!-- +- -->	
	<xsl:template match="aws:Item">
		<xsl:text> {</xsl:text>
		<xsl:text>"asin":"</xsl:text><xsl:value-of select="aws:ASIN"/><xsl:text>",</xsl:text>
		<xsl:text>"author_url":"</xsl:text><xsl:value-of select="aws:DetailPageURL"/><xsl:text>",</xsl:text>
                <xsl:text>"author_name":"</xsl:text><xsl:value-of select="aws:ItemAttributes/aws:Author"/><xsl:text>",</xsl:text>
		<xsl:text>"title":"</xsl:text><xsl:apply-templates select="aws:ItemAttributes/aws:Title"/><xsl:text>",</xsl:text>
		<xsl:text>"thumbnail_url":"</xsl:text><xsl:value-of select="aws:SmallImage/aws:URL"/><xsl:text>",</xsl:text>
		<xsl:text>"thumbnail_height":"</xsl:text><xsl:value-of select="aws:SmallImage/aws:Height"/><xsl:text>",</xsl:text>
		<xsl:text>"thumbnail_width":"</xsl:text><xsl:value-of select="aws:SmallImage/aws:Width"/><xsl:text>",</xsl:text>
                <xsl:text>"img_large": {</xsl:text>
                    <xsl:text>"height":"</xsl:text><xsl:value-of select="aws:LargeImage/aws:Height"/><xsl:text>",</xsl:text>
                    <xsl:text>"width":"</xsl:text><xsl:value-of select="aws:LargeImage/aws:Width"/><xsl:text>",</xsl:text>
                    <xsl:text>"url":"</xsl:text><xsl:value-of select="aws:LargeImage/aws:URL"/><xsl:text>"</xsl:text>
                <xsl:text>},</xsl:text>
                <xsl:text>"img_medium": {</xsl:text>
                    <xsl:text>"height":"</xsl:text><xsl:value-of select="aws:MediumImage/aws:Height"/><xsl:text>",</xsl:text>
                    <xsl:text>"width":"</xsl:text><xsl:value-of select="aws:MediumImage/aws:Width"/><xsl:text>",</xsl:text>
                    <xsl:text>"url":"</xsl:text><xsl:value-of select="aws:MediumImage/aws:URL"/><xsl:text>"</xsl:text>
                <xsl:text>},</xsl:text>
                <xsl:text>"img_small": {</xsl:text>
                    <xsl:text>"height":"</xsl:text><xsl:value-of select="aws:SmallImage/aws:Height"/><xsl:text>",</xsl:text>
                    <xsl:text>"width":"</xsl:text><xsl:value-of select="aws:SmallImage/aws:Width"/><xsl:text>",</xsl:text>
                    <xsl:text>"url":"</xsl:text><xsl:value-of select="aws:SmallImage/aws:URL"/><xsl:text>"</xsl:text>
                <xsl:text>}</xsl:text>
		<xsl:text>} </xsl:text>
	</xsl:template>

<!-- +- -->
<!-- | Title Template, used to strip out quotation marks (which would break the javascript) -->
<!-- +- -->	
	<xsl:template match="aws:Title">
		<xsl:call-template name="find-and-replace">
			<xsl:with-param name="str" select="."/>
			<xsl:with-param name="target">"</xsl:with-param>
			<xsl:with-param name="replacement" select="''"/>
		</xsl:call-template>
	</xsl:template>

<!-- +- -->
<!-- | Description Template, used to strip out quotation marks, newlines (which would break the javascript) -->
<!-- +- -->	
	<xsl:template match="aws:Content">
		<xsl:variable name="x">	
			<xsl:call-template name="find-and-replace">
				<xsl:with-param name="str" select="."/>
				<xsl:with-param name="target">"</xsl:with-param>
				<xsl:with-param name="replacement" select="''"/>
			</xsl:call-template>
		</xsl:variable>
		<xsl:variable name="y">
			<xsl:call-template name="find-and-replace">
				<xsl:with-param name="str" select="string($x)"/>
				<xsl:with-param name="target" select="'&#10;'"/>
				<xsl:with-param name="replacement" select="''"/>
			</xsl:call-template>		
		</xsl:variable>
		<xsl:variable name="z">
			<xsl:call-template name="find-and-replace">
				<xsl:with-param name="str" select="string($y)"/>
				<xsl:with-param name="target" select="'&#13;'"/>
				<xsl:with-param name="replacement" select="''"/>
			</xsl:call-template>		
		</xsl:variable>		
		<xsl:value-of select="$z"/>		
	</xsl:template>	

<!-- +- -->
<!-- | Search-and-Replace Template, swaps one string (target) with another (replacement) -->
<!-- +- -->	
	<xsl:template name="find-and-replace">
		<xsl:param name="str"/>
		<xsl:param name="target"/>
		<xsl:param name="replacement"/>
		<xsl:choose>
			<xsl:when test="$target and contains($str, $target)">
				<xsl:value-of select="substring-before($str, $target)" disable-output-escaping="yes"/>
				<xsl:value-of select="$replacement" disable-output-escaping="yes"/>
				<xsl:call-template name="find-and-replace">
					<xsl:with-param name="str" select="substring-after($str, $target)"/>
					<xsl:with-param name="target" select="$target"/>
					<xsl:with-param name="replacement" select="$replacement"/>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$str" disable-output-escaping="yes"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>	
	
</xsl:stylesheet>





