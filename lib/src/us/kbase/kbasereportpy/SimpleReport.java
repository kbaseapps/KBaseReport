
package us.kbase.kbasereportpy;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: SimpleReport</p>
 * <pre>
 * * A simple report for use in create()
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "text_message",
    "warnings",
    "direct_html"
})
public class SimpleReport {

    @JsonProperty("text_message")
    private java.lang.String textMessage;
    @JsonProperty("warnings")
    private List<String> warnings;
    @JsonProperty("direct_html")
    private java.lang.String directHtml;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("text_message")
    public java.lang.String getTextMessage() {
        return textMessage;
    }

    @JsonProperty("text_message")
    public void setTextMessage(java.lang.String textMessage) {
        this.textMessage = textMessage;
    }

    public SimpleReport withTextMessage(java.lang.String textMessage) {
        this.textMessage = textMessage;
        return this;
    }

    @JsonProperty("warnings")
    public List<String> getWarnings() {
        return warnings;
    }

    @JsonProperty("warnings")
    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }

    public SimpleReport withWarnings(List<String> warnings) {
        this.warnings = warnings;
        return this;
    }

    @JsonProperty("direct_html")
    public java.lang.String getDirectHtml() {
        return directHtml;
    }

    @JsonProperty("direct_html")
    public void setDirectHtml(java.lang.String directHtml) {
        this.directHtml = directHtml;
    }

    public SimpleReport withDirectHtml(java.lang.String directHtml) {
        this.directHtml = directHtml;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((("SimpleReport"+" [textMessage=")+ textMessage)+", warnings=")+ warnings)+", directHtml=")+ directHtml)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
