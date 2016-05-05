
package us.kbase.kbasereport;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: CreateReportParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report",
    "workspace_name"
})
public class CreateReportParams {

    /**
     * <p>Original spec-file type: Report</p>
     * <pre>
     * A simple Report of a method run in KBase.
     * It only provides for now a way to display a fixed width text output summary message, a 
     * list of warnings, and a list of objects created (each with descriptions).
     * @optional warnings
     * @metadata ws length(warnings) as Warnings
     * @metadata ws length(text_message) as Size(characters)
     * @metadata ws length(objects_created) as Objects Created
     * </pre>
     * 
     */
    @JsonProperty("report")
    private Report report;
    @JsonProperty("workspace_name")
    private String workspaceName;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    /**
     * <p>Original spec-file type: Report</p>
     * <pre>
     * A simple Report of a method run in KBase.
     * It only provides for now a way to display a fixed width text output summary message, a 
     * list of warnings, and a list of objects created (each with descriptions).
     * @optional warnings
     * @metadata ws length(warnings) as Warnings
     * @metadata ws length(text_message) as Size(characters)
     * @metadata ws length(objects_created) as Objects Created
     * </pre>
     * 
     */
    @JsonProperty("report")
    public Report getReport() {
        return report;
    }

    /**
     * <p>Original spec-file type: Report</p>
     * <pre>
     * A simple Report of a method run in KBase.
     * It only provides for now a way to display a fixed width text output summary message, a 
     * list of warnings, and a list of objects created (each with descriptions).
     * @optional warnings
     * @metadata ws length(warnings) as Warnings
     * @metadata ws length(text_message) as Size(characters)
     * @metadata ws length(objects_created) as Objects Created
     * </pre>
     * 
     */
    @JsonProperty("report")
    public void setReport(Report report) {
        this.report = report;
    }

    public CreateReportParams withReport(Report report) {
        this.report = report;
        return this;
    }

    @JsonProperty("workspace_name")
    public String getWorkspaceName() {
        return workspaceName;
    }

    @JsonProperty("workspace_name")
    public void setWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
    }

    public CreateReportParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((("CreateReportParams"+" [report=")+ report)+", workspaceName=")+ workspaceName)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
