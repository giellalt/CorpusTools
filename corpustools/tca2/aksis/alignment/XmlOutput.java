/*
 * XmlOutput.java
 *
 * ...
 * ...
 * ...
 */

package aksis.alignment;

import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.Templates;
import javax.xml.transform.stream.*;
import java.io.*;
import org.w3c.dom.*;
import java.nio.charset.*;
import javax.xml.transform.OutputKeys;



/**
 *
 * @author Johan Utne Poppe
 */

class XmlOutput {

	//static void writeXml(Document d, File f) {
	static void writeXml(Document d, File f, Charset cs) {

		//System.out.println("f er " + f + ". cs er " + cs.toString());

		try {

			// Use a Transformer for output
			TransformerFactory tFactory = TransformerFactory.newInstance();

			//¤¤¤et forsøk på å få riktig encoding på outputfil ved å bruke et stilark.
			//¤¤¤det blir riktig encoding, men xml-kodingen forsvinner.
			//¤¤¤dvs det siste går kanskje an å fikse,
			//¤¤¤men transformasjon vil kanskje gjøre om entities, og det vil vi ikke?
			//// Use the factory to read the XSLT ¤¤¤file into a Templates object
			//StreamSource xsltSource = new StreamSource(new StringReader("<xsl:stylesheet version='1.0'\n                xmlns:xsl='http://www.w3.org/1999/XSL/Transform'\n                xmlns='http://www.w3.org/TR/xhtml1/strict'>\n  <xsl:output method='xml' encoding='iso-8859-1'/>\n  <xsl:template match='/'>\n    <xsl:apply-templates/>\n  </xsl:template>\n</xsl:stylesheet>"));
			//Templates transformation = tFactory.newTemplates(xsltSource);
			//// Create a Transformer object from the Templates object
			//Transformer transformer = transformation.newTransformer();

			Transformer transformer = tFactory.newTransformer();
			transformer.setOutputProperty(OutputKeys.ENCODING, cs.toString());

			DOMSource source = new DOMSource(d);

			//StreamResult result = new StreamResult(new FileWriter(f));
			//¤¤¤endringer 2006-02-20 for å kunne skrive utf-8, o.a
			OutputStream fOut= new FileOutputStream(f);
			OutputStream bOut= new BufferedOutputStream(fOut);
			OutputStreamWriter out = new OutputStreamWriter(bOut, cs);
			StreamResult result = new StreamResult(out);

			// Finally, perform the transformation
			transformer.transform(source, result);

		} catch (TransformerConfigurationException tce) {

			// Error generated by the parser
			System.out.println ("*** Transformer Factory error: " + tce.getMessage());

			// Use the contained exception, if any
			Throwable x = tce;
			if (tce.getException() != null) {
				x = tce.getException();
			}
			x.printStackTrace();

		} catch (TransformerException te) {

			// Error generated by the parser
			System.out.println ("*** Transformation error: " + te.getMessage());

			// Use the contained exception, if any
			Throwable x = te;
			if (te.getException() != null) {
				x = te.getException();
			}
			x.printStackTrace();

		/*} catch (SAXParseException spe) {

			// Error generated by the parser
			System.out.println("\n** Parsing error"
				+ ", line " + spe.getLineNumber()
				+ ", uri " + spe.getSystemId());
			System.out.println("   " + spe.getMessage() );

			// Use the contained exception, if any
			Exception  x = spe;
			if (spe.getException() != null) {
				x = spe.getException();
			}
			x.printStackTrace();

		} catch (SAXException sxe) {

			// Error generated by this application
			// (or a parser-initialization error)
			Exception  x = sxe;
			if (sxe.getException() != null) {
				x = sxe.getException();
			}
			x.printStackTrace();

		} catch (ParserConfigurationException pce) {

			// Parser with specified options can't be built
			pce.printStackTrace();
		*/

		} catch (IOException ioe) {

			// I/O error
			ioe.printStackTrace();

		}

	}


} //end class XmlOutput