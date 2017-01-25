<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <!--PROXY-->
  <profiles>
    <profile>
      <id>public</id>
      <repositories>
        <repository>
          <id>normation-releases</id>
          <url>http://www.rudder-project.org/maven-releases/</url>
          <releases><enabled>true</enabled></releases>
        </repository>
        <repository>
          <id>normation-snapshots</id>
          <url>http://www.rudder-project.org/maven-snapshots/</url>
          <snapshots><enabled>true</enabled></snapshots>
        </repository>
      </repositories>
    </profile>
  </profiles>
  <activeProfiles>
    <activeProfile>public</activeProfile>
  </activeProfiles>
</settings>
