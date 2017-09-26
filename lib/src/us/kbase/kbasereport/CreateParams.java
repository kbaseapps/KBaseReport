
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
 * <p>Original spec-file type: CreateParams</p>
 * <pre>
 * Provide the report information. Either workspace name or workspace id is required  The structure is:
 *     params = {
 *         report: {
 *             text_message: '',
 *             warnings: ['w1'],
 *             objects_created: [ {
 *                 ref: 'ws/objid',
 *                 description: ''
 *             }]
 *         },
 *         workspace_name: 'ws'
 *         workspace_id: id
 *     }
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report",
    "workspace_name",
    "workspace_id"
})
public class CreateParams {

    /**
     * <p>Original spec-file type: Report</p>
     * <pre>
     * A simple Report of a method run in KBase.
     * It only provides for now a way to display a fixed width text output summary message, a
     * list of warnings, and a list of objects created (each with descriptions).
     * @optional warnings file_links html_links direct_html direct_html_link_index
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
    @JsonProperty("workspace_id")
    private Long workspaceId;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    /**
     * <p>Original spec-file type: Report</p>
     * <pre>
     * A simple Report of a method run in KBase.
     * It only provides for now a way to display a fixed width text output summary message, a
     * list of warnings, and a list of objects created (each with descriptions).
     * @optional warnings file_links html_links direct_html direct_html_link_index
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
     * @optional warnings file_links html_links direct_html direct_html_link_index
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

    public CreateParams withReport(Report report) {
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

    public CreateParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonProperty("workspace_id")
    public Long getWorkspaceId() {
        return workspaceId;
    }

    @JsonProperty("workspace_id")
    public void setWorkspaceId(Long workspaceId) {
        this.workspaceId = workspaceId;
    }

    public CreateParams withWorkspaceId(Long workspaceId) {
        this.workspaceId = workspaceId;
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
        return ((((((((("CreateParams"+" [report=")+ report)+", workspaceName=")+ workspaceName)+", workspaceId=")+ workspaceId)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
