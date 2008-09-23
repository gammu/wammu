<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" media-type="text/html; charset=UTF-8"/>

<xsl:template match="/messages">
<html>
	<style type="text/css">
	div.sms  {
		margin: 0.75em 5px;
		background-color: #d2ddf6;
		border: solid 2px black;
	}
	div.telephone  {
		font-weight: bold;
	}
	div.text {
		color: #CC0000;
	}
	div{
		margin: 0.25em 0px;
	}
	</style>

	<h1>Messages Recus</h1>

	<xsl:for-each select="message">
		<xsl:sort   select="dateenc"/>
		<xsl:variable name="stat" select="stat"/>
		


		<xsl:if test="$stat='Read'">

		<div class="sms">
			<div class="telephone"><xsl:value-of select="telephone"/></div>
			<div class="date"> <xsl:value-of select="date"/></div>
			<div class="text"> <xsl:value-of select="text"/></div>
		</div>

		</xsl:if>

	</xsl:for-each>

	<h1>Messages Envoyés</h1>

	<xsl:for-each select="message">
		<xsl:sort   select="dateenc"/>
		<xsl:variable name="stat" select="stat"/>
		


		<xsl:if test="$stat='Sent'">

		<div class="sms">
			<div class="telephone"><xsl:value-of select="telephone"/></div>
			<div class="date"> <xsl:value-of select="date"/></div>
			<div class="text"> <xsl:value-of select="text"/></div>
		</div>

		</xsl:if>

	</xsl:for-each>

</html>
</xsl:template>

</xsl:stylesheet>
