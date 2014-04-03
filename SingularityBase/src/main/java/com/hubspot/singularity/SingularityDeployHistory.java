package com.hubspot.singularity;

import java.io.IOException;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Optional;

public class SingularityDeployHistory extends SingularityJsonObject {
  
  private final Optional<DeployState> deployState;
  private final SingularityDeployMarker deployMarker;
  private final SingularityDeploy deploy;
  private final Optional<SingularityDeployStatistics> deployStatistics;
  
  public static SingularityDeployHistory fromBytes(byte[] bytes, ObjectMapper objectMapper) {
    try {
      return objectMapper.readValue(bytes, SingularityDeployHistory.class);
    } catch (IOException e) {
      throw new SingularityJsonException(e);
    }
  }
  
  @JsonCreator
  public SingularityDeployHistory(@JsonProperty("deployState") Optional<DeployState> deployState, @JsonProperty("deployMarker") SingularityDeployMarker deployMarker, 
      @JsonProperty("deploy") SingularityDeploy deploy, @JsonProperty("deployStatistics") Optional<SingularityDeployStatistics> deployStatistics) {
    this.deployState = deployState;
    this.deployMarker = deployMarker;
    this.deploy = deploy;
    this.deployStatistics = deployStatistics;
  }

  public Optional<DeployState> getDeployState() {
    return deployState;
  }

  public SingularityDeployMarker getDeployMarker() {
    return deployMarker;
  }

  public SingularityDeploy getDeploy() {
    return deploy;
  }

  public Optional<SingularityDeployStatistics> getDeployStatistics() {
    return deployStatistics;
  }

  @Override
  public String toString() {
    return "SingularityDeployHistory [deployState=" + deployState + ", deployMarker=" + deployMarker + ", deploy=" + deploy + ", deployStatistics=" + deployStatistics + "]";
  }
  
}
