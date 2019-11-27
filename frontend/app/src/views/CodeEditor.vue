<template>
  <div class="wrapper">
    <div class="animated fadeIn">
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> General information
            </div>
            <div class="card-block">

            <div class="row">
<label class="col-sm-2">Revision</label>

<div class="col-sm-10">
            <a href="#">Show 26c458f09bc858537d02b3749868e8318b167a68 on GitHub</a>
            </div>
            </div>

            <div class="row">
<label class="col-sm-2">Issue Links</label>
<div class="col-sm-10">
            <a href="#">IVY-1150</a>
            </div>
            </div>


<div class="row">
<label class="col-sm-2">Commit Message</label>
<div class="col-sm-10">
            <textarea class="form-control">FIX: Artifact report throws NPE when artifact is not in cache (IVY-1150) (thanks to Steve Jones)

git-svn-id: https://svn.apache.org/repos/asf/ant/ivy/core/trunk@892370 13f79535-47bb-0310-9956-ffa450edef68</textarea>
            </div>
            </div>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <i class="fa fa-bug"></i> Changes
            </div>
            <div class="card-block">
             <MonacoEditor class="editor"
  :diffEditor="true" :value="code" :original="original" language="java" ref="editor" />
            </div>
          </div>

    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import MonacoEditor from 'vue-monaco'



export default {
  data () {
  var jsCode2 = `/*
 *  Licensed to the Apache Software Foundation (ASF) under one or more
 *  contributor license agreements.  See the NOTICE file distributed with
 *  this work for additional information regarding copyright ownership.
 *  The ASF licenses this file to You under the Apache License, Version 2.0
 *  (the "License"); you may not use this file except in compliance with
 *  the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 */
package org.apache.ivy.ant;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.ParseException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import javax.xml.transform.OutputKeys;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerFactoryConfigurationError;
import javax.xml.transform.sax.SAXTransformerFactory;
import javax.xml.transform.sax.TransformerHandler;
import javax.xml.transform.stream.StreamResult;

import org.apache.ivy.core.cache.ArtifactOrigin;
import org.apache.ivy.core.cache.RepositoryCacheManager;
import org.apache.ivy.core.module.descriptor.Artifact;
import org.apache.ivy.core.module.descriptor.ModuleDescriptor;
import org.apache.ivy.core.module.id.ModuleRevisionId;
import org.apache.ivy.core.report.ArtifactDownloadReport;
import org.apache.ivy.core.resolve.IvyNode;
import org.apache.ivy.core.resolve.ResolveOptions;
import org.apache.ivy.core.resolve.ResolvedModuleRevision;
import org.apache.ivy.core.retrieve.RetrieveOptions;
import org.apache.tools.ant.BuildException;
import org.apache.tools.ant.Project;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.AttributesImpl;

/**
 * Generates a report of all artifacts involved during the last resolve.
 */
public class IvyArtifactReport extends IvyPostResolveTask {
    private File tofile;

    private String pattern;

    public File getTofile() {
        return tofile;
    }

    public void setTofile(File aFile) {
        tofile = aFile;
    }

    public String getPattern() {
        return pattern;
    }

    public void setPattern(String aPattern) {
        pattern = aPattern;
    }

    public void doExecute() throws BuildException {
        prepareAndCheck();
        if (tofile == null) {
            throw new BuildException(
                    "no destination file name: please provide it through parameter 'tofile'");
        }

        pattern = getProperty(pattern, getSettings(), "ivy.retrieve.pattern");

        try {
            String[] confs = splitConfs(getConf());
            ModuleDescriptor md = null;
            if (getResolveId() != null) {
                md = (ModuleDescriptor) getResolvedDescriptor(getResolveId());
            } else {
                md = (ModuleDescriptor) getResolvedDescriptor(getOrganisation(), getModule()
                        , false);
            }
            IvyNode[] dependencies = getIvyInstance().getResolveEngine().getDependencies(
                md,
                new ResolveOptions().setConfs(confs).setResolveId(
                    getResolveId()).setValidate(doValidate(getSettings())), null);

            Map artifactsToCopy = getIvyInstance().getRetrieveEngine().determineArtifactsToCopy(
                ModuleRevisionId.newInstance(getOrganisation(), getModule(), getRevision()),
                pattern,
                new RetrieveOptions().setConfs(confs).setResolveId(getResolveId()));

            Map moduleRevToArtifactsMap = new HashMap();
            for (Iterator iter = artifactsToCopy.keySet().iterator(); iter.hasNext();) {
                ArtifactDownloadReport artifact = (ArtifactDownloadReport) iter.next();
                Set moduleRevArtifacts = (Set) moduleRevToArtifactsMap.get(artifact.getArtifact()
                        .getModuleRevisionId());
                if (moduleRevArtifacts == null) {
                    moduleRevArtifacts = new HashSet();
                    moduleRevToArtifactsMap.put(
                        artifact.getArtifact().getModuleRevisionId(), moduleRevArtifacts);
                }
                moduleRevArtifacts.add(artifact);
            }

            generateXml(dependencies, moduleRevToArtifactsMap, artifactsToCopy);
        } catch (ParseException e) {
            log(e.getMessage(), Project.MSG_ERR);
            throw new BuildException("syntax errors in ivy file: " + e, e);
        } catch (IOException e) {
            throw new BuildException("impossible to generate report: " + e, e);
        }
    }

    private void generateXml(IvyNode[] dependencies,
            Map moduleRevToArtifactsMap, Map artifactsToCopy) {
        try {
            FileOutputStream fileOuputStream = new FileOutputStream(tofile);
            try {
                TransformerHandler saxHandler = createTransformerHandler(fileOuputStream);

                saxHandler.startDocument();
                saxHandler.startElement(null, "modules", "modules", new AttributesImpl());

                for (int i = 0; i < dependencies.length; i++) {
                    IvyNode dependency = dependencies[i];
                    if (dependency.getModuleRevision() == null
                            || dependency.isCompletelyEvicted()) {
                        continue;
                    }

                    startModule(saxHandler, dependency);

                    Set artifactsOfModuleRev = (Set) moduleRevToArtifactsMap.get(dependency
                            .getModuleRevision().getId());
                    if (artifactsOfModuleRev != null) {
                        for (Iterator iter = artifactsOfModuleRev.iterator(); iter.hasNext();) {
                            ArtifactDownloadReport artifact = (ArtifactDownloadReport) iter.next();

                            RepositoryCacheManager cache = dependency.getModuleRevision()
                                .getArtifactResolver().getRepositoryCacheManager();

                            startArtifact(saxHandler, artifact.getArtifact());

                            writeOriginLocationIfPresent(cache, saxHandler, artifact);
                            writeCacheLocationIfPresent(cache, saxHandler, artifact);

                            Set artifactDestPaths = (Set) artifactsToCopy.get(artifact);
                            for (Iterator iterator = artifactDestPaths.iterator(); iterator
                                    .hasNext();) {
                                String artifactDestPath = (String) iterator.next();
                                writeRetrieveLocation(saxHandler, artifactDestPath);
                            }
                            saxHandler.endElement(null, "artifact", "artifact");
                        }
                    }
                    saxHandler.endElement(null, "module", "module");
                }
                saxHandler.endElement(null, "modules", "modules");
                saxHandler.endDocument();
            } finally {
                fileOuputStream.close();
            }
        } catch (SAXException e) {
            throw new BuildException("impossible to generate report", e);
        } catch (TransformerConfigurationException e) {
            throw new BuildException("impossible to generate report", e);
        } catch (IOException e) {
            throw new BuildException("impossible to generate report", e);
        }
    }

    private TransformerHandler createTransformerHandler(FileOutputStream fileOuputStream)
            throws TransformerFactoryConfigurationError, TransformerConfigurationException,
            SAXException {
        SAXTransformerFactory transformerFact = (SAXTransformerFactory) SAXTransformerFactory
                .newInstance();
        TransformerHandler saxHandler = transformerFact.newTransformerHandler();
        saxHandler.getTransformer().setOutputProperty(OutputKeys.ENCODING, "UTF-8");
        saxHandler.getTransformer().setOutputProperty(OutputKeys.INDENT, "yes");
        saxHandler.setResult(new StreamResult(fileOuputStream));
        return saxHandler;
    }

    private void startModule(TransformerHandler saxHandler, IvyNode dependency)
            throws SAXException {
        AttributesImpl moduleAttrs = new AttributesImpl();
        moduleAttrs.addAttribute(null, "organisation", "organisation", "CDATA", dependency
                .getModuleId().getOrganisation());
        moduleAttrs.addAttribute(null, "name", "name", "CDATA", dependency.getModuleId().getName());
        ResolvedModuleRevision moduleRevision = dependency.getModuleRevision();
        moduleAttrs.addAttribute(null, "rev", "rev", "CDATA", moduleRevision
                .getId().getRevision());
        moduleAttrs.addAttribute(null, "status", "status", "CDATA", moduleRevision
                .getDescriptor().getStatus());
        saxHandler.startElement(null, "module", "module", moduleAttrs);
    }

    private void startArtifact(TransformerHandler saxHandler, Artifact artifact)
            throws SAXException {
        AttributesImpl artifactAttrs = new AttributesImpl();
        artifactAttrs.addAttribute(null, "name", "name", "CDATA", artifact.getName());
        artifactAttrs.addAttribute(null, "ext", "ext", "CDATA", artifact.getExt());
        artifactAttrs.addAttribute(null, "type", "type", "CDATA", artifact.getType());
        saxHandler.startElement(null, "artifact", "artifact", artifactAttrs);
    }

    private void writeOriginLocationIfPresent(
            RepositoryCacheManager cache, TransformerHandler saxHandler,
            ArtifactDownloadReport artifact)
            throws IOException, SAXException {
        ArtifactOrigin origin = artifact.getArtifactOrigin();
        if (!ArtifactOrigin.isUnknown(origin)) {
            String originName = origin.getLocation();
            boolean isOriginLocal = origin.isLocal();

            String originLocation;
            AttributesImpl originLocationAttrs = new AttributesImpl();
            if (isOriginLocal) {
                originLocationAttrs.addAttribute(null, "is-local", "is-local", "CDATA", "true");
                originLocation = originName.replace('\\', '/');
            } else {
                originLocationAttrs.addAttribute(null, "is-local", "is-local", "CDATA", "false");
                originLocation = originName;
            }
            saxHandler
                    .startElement(null, "origin-location", "origin-location", originLocationAttrs);
            char[] originLocationAsChars = originLocation.toCharArray();
            saxHandler.characters(originLocationAsChars, 0, originLocationAsChars.length);
            saxHandler.endElement(null, "origin-location", "origin-location");
        }
    }

    private void writeCacheLocationIfPresent(RepositoryCacheManager cache, TransformerHandler saxHandler,
            ArtifactDownloadReport artifact) throws SAXException {
        File archiveInCache = artifact.getLocalFile();

        if (archiveInCache != null) {
            saxHandler.startElement(null, "cache-location", "cache-location", new AttributesImpl());
            char[] archiveInCacheAsChars = archiveInCache.getPath().replace('\\', '/').toCharArray();
            saxHandler.characters(archiveInCacheAsChars, 0, archiveInCacheAsChars.length);
            saxHandler.endElement(null, "cache-location", "cache-location");
        }
    }

    private void writeRetrieveLocation(TransformerHandler saxHandler, String artifactDestPath)
            throws SAXException {
        artifactDestPath = removeLeadingPath(getProject().getBaseDir(), new File(artifactDestPath));

        saxHandler.startElement(null, "retrieve-location", "retrieve-location",
            new AttributesImpl());
        char[] artifactDestPathAsChars = artifactDestPath.replace('\\', '/').toCharArray();
        saxHandler.characters(artifactDestPathAsChars, 0, artifactDestPathAsChars.length);
        saxHandler.endElement(null, "retrieve-location", "retrieve-location");
    }

    // method largely inspired by ant 1.6.5 FileUtils method
    public String removeLeadingPath(File leading, File path) {
        String l = leading.getAbsolutePath();
        String p = path.getAbsolutePath();
        if (l.equals(p)) {
            return "";
        }

        // ensure that l ends with a /
        // so we never think /foo was a parent directory of /foobar
        if (!l.endsWith(File.separator)) {
            l += File.separator;
        }
        return (p.startsWith(l)) ? p.substring(l.length()) : p;
    }

}`;

  var jsCode = `/*
 *  Licensed to the Apache Software Foundation (ASF) under one or more
 *  contributor license agreements.  See the NOTICE file distributed with
 *  this work for additional information regarding copyright ownership.
 *  The ASF licenses this file to You under the Apache License, Version 2.0
 *  (the "License"); you may not use this file except in compliance with
 *  the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 */
package org.apache.ivy.ant;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.ParseException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import javax.xml.transform.OutputKeys;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerFactoryConfigurationError;
import javax.xml.transform.sax.SAXTransformerFactory;
import javax.xml.transform.sax.TransformerHandler;
import javax.xml.transform.stream.StreamResult;

import org.apache.ivy.core.cache.ArtifactOrigin;
import org.apache.ivy.core.cache.RepositoryCacheManager;
import org.apache.ivy.core.module.descriptor.Artifact;
import org.apache.ivy.core.module.descriptor.ModuleDescriptor;
import org.apache.ivy.core.module.id.ModuleRevisionId;
import org.apache.ivy.core.report.ArtifactDownloadReport;
import org.apache.ivy.core.resolve.IvyNode;
import org.apache.ivy.core.resolve.ResolveOptions;
import org.apache.ivy.core.resolve.ResolvedModuleRevision;
import org.apache.ivy.core.retrieve.RetrieveOptions;
import org.apache.tools.ant.BuildException;
import org.apache.tools.ant.Project;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.AttributesImpl;

/**
 * Generates a report of all artifacts involved during the last resolve.
 */
public class IvyArtifactReport extends IvyPostResolveTask {
    private File tofile;

    private String pattern;

    public File getTofile() {
        return tofile;
    }

    public void setTofile(File aFile) {
        tofile = aFile;
    }

    public String getPattern() {
        return pattern;
    }

    public void setPattern(String aPattern) {
        pattern = aPattern;
    }

    public void doExecute() throws BuildException {
        prepareAndCheck();
        if (tofile == null) {
            throw new BuildException(
                    "no destination file name: please provide it through parameter 'tofile'");
        }

        pattern = getProperty(pattern, getSettings(), "ivy.retrieve.pattern");

        try {
            String[] confs = splitConfs(getConf());
            ModuleDescriptor md = null;
            if (getResolveId() != null) {
                md = (ModuleDescriptor) getResolvedDescriptor(getResolveId());
            } else {
                md = (ModuleDescriptor) getResolvedDescriptor(getOrganisation(), getModule()
                        , false);
            }
            IvyNode[] dependencies = getIvyInstance().getResolveEngine().getDependencies(
                md,
                new ResolveOptions().setConfs(confs).setResolveId(
                    getResolveId()).setValidate(doValidate(getSettings())), null);

            Map artifactsToCopy = getIvyInstance().getRetrieveEngine().determineArtifactsToCopy(
                ModuleRevisionId.newInstance(getOrganisation(), getModule(), getRevision()),
                pattern,
                new RetrieveOptions().setConfs(confs).setResolveId(getResolveId()));

            Map moduleRevToArtifactsMap = new HashMap();
            for (Iterator iter = artifactsToCopy.keySet().iterator(); iter.hasNext();) {
                ArtifactDownloadReport artifact = (ArtifactDownloadReport) iter.next();
                Set moduleRevArtifacts = (Set) moduleRevToArtifactsMap.get(artifact.getArtifact()
                        .getModuleRevisionId());
                if (moduleRevArtifacts == null) {
                    moduleRevArtifacts = new HashSet();
                    moduleRevToArtifactsMap.put(
                        artifact.getArtifact().getModuleRevisionId(), moduleRevArtifacts);
                }
                moduleRevArtifacts.add(artifact);
            }

            generateXml(dependencies, moduleRevToArtifactsMap, artifactsToCopy);
        } catch (ParseException e) {
            log(e.getMessage(), Project.MSG_ERR);
            throw new BuildException("syntax errors in ivy file: " + e, e);
        } catch (IOException e) {
            throw new BuildException("impossible to generate report: " + e, e);
        }
    }

    private void generateXml(IvyNode[] dependencies,
            Map moduleRevToArtifactsMap, Map artifactsToCopy) {
        try {
            FileOutputStream fileOuputStream = new FileOutputStream(tofile);
            try {
                TransformerHandler saxHandler = createTransformerHandler(fileOuputStream);

                saxHandler.startDocument();
                saxHandler.startElement(null, "modules", "modules", new AttributesImpl());

                for (int i = 0; i < dependencies.length; i++) {
                    IvyNode dependency = dependencies[i];
                    if (dependency.getModuleRevision() == null
                            || dependency.isCompletelyEvicted()) {
                        continue;
                    }

                    startModule(saxHandler, dependency);

                    Set artifactsOfModuleRev = (Set) moduleRevToArtifactsMap.get(dependency
                            .getModuleRevision().getId());
                    if (artifactsOfModuleRev != null) {
                        for (Iterator iter = artifactsOfModuleRev.iterator(); iter.hasNext();) {
                            ArtifactDownloadReport artifact = (ArtifactDownloadReport) iter.next();

                            RepositoryCacheManager cache = dependency.getModuleRevision()
                                .getArtifactResolver().getRepositoryCacheManager();

                            startArtifact(saxHandler, artifact.getArtifact());

                            writeOriginLocationIfPresent(cache, saxHandler, artifact);

                            writeCacheLocation(cache, saxHandler, artifact);

                            Set artifactDestPaths = (Set) artifactsToCopy.get(artifact);
                            for (Iterator iterator = artifactDestPaths.iterator(); iterator
                                    .hasNext();) {
                                String artifactDestPath = (String) iterator.next();
                                writeRetrieveLocation(saxHandler, artifactDestPath);
                            }
                            saxHandler.endElement(null, "artifact", "artifact");
                        }
                    }
                    saxHandler.endElement(null, "module", "module");
                }
                saxHandler.endElement(null, "modules", "modules");
                saxHandler.endDocument();
            } finally {
                fileOuputStream.close();
            }
        } catch (SAXException e) {
            throw new BuildException("impossible to generate report", e);
        } catch (TransformerConfigurationException e) {
            throw new BuildException("impossible to generate report", e);
        } catch (IOException e) {
            throw new BuildException("impossible to generate report", e);
        }
    }

    private TransformerHandler createTransformerHandler(FileOutputStream fileOuputStream)
            throws TransformerFactoryConfigurationError, TransformerConfigurationException,
            SAXException {
        SAXTransformerFactory transformerFact = (SAXTransformerFactory) SAXTransformerFactory
                .newInstance();
        TransformerHandler saxHandler = transformerFact.newTransformerHandler();
        saxHandler.getTransformer().setOutputProperty(OutputKeys.ENCODING, "UTF-8");
        saxHandler.getTransformer().setOutputProperty(OutputKeys.INDENT, "yes");
        saxHandler.setResult(new StreamResult(fileOuputStream));
        return saxHandler;
    }

    private void startModule(TransformerHandler saxHandler, IvyNode dependency)
            throws SAXException {
        AttributesImpl moduleAttrs = new AttributesImpl();
        moduleAttrs.addAttribute(null, "organisation", "organisation", "CDATA", dependency
                .getModuleId().getOrganisation());
        moduleAttrs.addAttribute(null, "name", "name", "CDATA", dependency.getModuleId().getName());
        ResolvedModuleRevision moduleRevision = dependency.getModuleRevision();
        moduleAttrs.addAttribute(null, "rev", "rev", "CDATA", moduleRevision
                .getId().getRevision());
        moduleAttrs.addAttribute(null, "status", "status", "CDATA", moduleRevision
                .getDescriptor().getStatus());
        saxHandler.startElement(null, "module", "module", moduleAttrs);
    }

    private void startArtifact(TransformerHandler saxHandler, Artifact artifact)
            throws SAXException {
        AttributesImpl artifactAttrs = new AttributesImpl();
        artifactAttrs.addAttribute(null, "name", "name", "CDATA", artifact.getName());
        artifactAttrs.addAttribute(null, "ext", "ext", "CDATA", artifact.getExt());
        artifactAttrs.addAttribute(null, "type", "type", "CDATA", artifact.getType());
        saxHandler.startElement(null, "artifact", "artifact", artifactAttrs);
    }

    private void writeOriginLocationIfPresent(
            RepositoryCacheManager cache, TransformerHandler saxHandler,
            ArtifactDownloadReport artifact)
            throws IOException, SAXException {
        ArtifactOrigin origin = artifact.getArtifactOrigin();
        if (!ArtifactOrigin.isUnknown(origin)) {
            String originName = origin.getLocation();
            boolean isOriginLocal = origin.isLocal();

            String originLocation;
            AttributesImpl originLocationAttrs = new AttributesImpl();
            if (isOriginLocal) {
                originLocationAttrs.addAttribute(null, "is-local", "is-local", "CDATA", "true");
                originLocation = originName.replace('\\', '/');
            } else {
                originLocationAttrs.addAttribute(null, "is-local", "is-local", "CDATA", "false");
                originLocation = originName;
            }
            saxHandler
                    .startElement(null, "origin-location", "origin-location", originLocationAttrs);
            char[] originLocationAsChars = originLocation.toCharArray();
            saxHandler.characters(originLocationAsChars, 0, originLocationAsChars.length);
            saxHandler.endElement(null, "origin-location", "origin-location");
        }
    }

    private void writeCacheLocation(RepositoryCacheManager cache, TransformerHandler saxHandler,
            ArtifactDownloadReport artifact) throws SAXException {
        File archiveInCache = artifact.getLocalFile();

        saxHandler.startElement(null, "cache-location", "cache-location", new AttributesImpl());
        char[] archiveInCacheAsChars = archiveInCache.getPath().replace('\\', '/').toCharArray();
        saxHandler.characters(archiveInCacheAsChars, 0, archiveInCacheAsChars.length);
        saxHandler.endElement(null, "cache-location", "cache-location");
    }

    private void writeRetrieveLocation(TransformerHandler saxHandler, String artifactDestPath)
            throws SAXException {
        artifactDestPath = removeLeadingPath(getProject().getBaseDir(), new File(artifactDestPath));

        saxHandler.startElement(null, "retrieve-location", "retrieve-location",
            new AttributesImpl());
        char[] artifactDestPathAsChars = artifactDestPath.replace('\\', '/').toCharArray();
        saxHandler.characters(artifactDestPathAsChars, 0, artifactDestPathAsChars.length);
        saxHandler.endElement(null, "retrieve-location", "retrieve-location");
    }

    // method largely inspired by ant 1.6.5 FileUtils method
    public String removeLeadingPath(File leading, File path) {
        String l = leading.getAbsolutePath();
        String p = path.getAbsolutePath();
        if (l.equals(p)) {
            return "";
        }

        // ensure that l ends with a /
        // so we never think /foo was a parent directory of /foobar
        if (!l.endsWith(File.separator)) {
            l += File.separator;
        }
        return (p.startsWith(l)) ? p.substring(l.length()) : p;
    }

}`;


    return {
      code: jsCode,
      original: jsCode2
    }
  },
  mounted () {

  var that2 = this;
  window.editor = this.$refs.editor;
  console.log("That2 log:");
  console.log(that2);
  var margin = 2;

  monaco.languages.registerFoldingRangeProvider("java", {
    provideFoldingRanges: function(model, context, token) {
        var ranges = [];
        console.log(model);
        console.log(context);
        console.log(that2);
        var startLine = 1;
        var isOrginial = window.editor.getEditor().getOriginalEditor().getModel() == model;
        var changes = window.editor.getEditor().getLineChanges();
        for(var i = 0; i < changes.length; i++)
        {
          var change = changes[i];
          var ende = change.originalStartLineNumber;
          if(ende > change.modifiedStartLineNumber)
          {
             ende = change.modifiedStartLineNumber;
          }
          ende = ende - margin;
          var range = {
                start: startLine,
                end: ende,
                kind: monaco.languages.FoldingRangeKind.Region
          };
          ranges.push(range);

          var newStartLine = change.originalEndLineNumber;
          if(newStartLine < change.modifiedEndLineNumber)
          {
             newStartLine = change.modifiedEndLineNumber;
          }
          if(newStartLine == 0)
          {
             newStartLine = ende +1;

          }
          startLine = newStartLine + margin;

        }

        ranges.push({
                start: startLine + margin,
                end: model.getLineCount(),
                kind: monaco.languages.FoldingRangeKind.Region
        });
        return ranges;
    }
});

     var ed = this.$refs.editor.getEditor().getOriginalEditor();
     var decorations = this.$refs.editor.getEditor().getOriginalEditor().deltaDecorations([], [
	{ range: new monaco.Range(1,1,3,1), options: { isWholeLine: true, linesDecorationsClassName: 'myLineDecoration' }},
]);
window.editor1 = this.$refs.editor;

this.$refs.editor.getEditor().getModifiedEditor().updateOptions({ readOnly: true, folding: true, automaticLayout: true  });
this.$refs.editor.getEditor().getOriginalEditor().updateOptions({ readOnly: true, folding: true,  automaticLayout: true  });
this.$refs.editor.getEditor().getOriginalEditor().addAction({
	// An unique identifier of the contributed action.
	id: 'my-unique-id',

	// A label of the action that will be presented to the user.
	label: 'Add Linelabel',

	// An optional array of keybindings for the action.
	keybindings: [		// chord
		 monaco.KeyCode.KEY_L
	],

	// A precondition for this action.
	precondition: null,

	// A rule to evaluate on top of the precondition in order to dispatch the keybindings.
	keybindingContext: null,

	contextMenuGroupId: 'navigation',

	contextMenuOrder: 1.5,

	// Method that will be executed when the action is triggered.
	// @param editor The editor instance is passed in as a convinience
	run: function(ed) {
	  var lineNumber = ed.getPosition().lineNumber;
	  ed.deltaDecorations([], [
	{ range: new monaco.Range(lineNumber,1,lineNumber,1), options: { isWholeLine: true, linesDecorationsClassName: 'myLineDecoration' }},
]);
		return null;
	}
});

this.$refs.editor.getEditor().getOriginalEditor().addAction({
	// An unique identifier of the contributed action.
	id: 'my-unique-id2',

	// A label of the action that will be presented to the user.
	label: 'Add Linelabel2',

	// An optional array of keybindings for the action.
	keybindings: [		// chord
		 monaco.KeyCode.KEY_K
	],

	// A precondition for this action.
	precondition: null,

	// A rule to evaluate on top of the precondition in order to dispatch the keybindings.
	keybindingContext: null,

	contextMenuGroupId: 'navigation',

	contextMenuOrder: 1.5,

	// Method that will be executed when the action is triggered.
	// @param editor The editor instance is passed in as a convinience
	run: function(ed) {
	  var lineNumber = ed.getPosition().lineNumber;
	  ed.deltaDecorations([], [
	{ range: new monaco.Range(lineNumber,1,lineNumber,1), options: { isWholeLine: true, linesDecorationsClassName: 'myLineDecoration2' }},
]);
		return null;
	}
});

var foldingContrib = that2.$refs.editor.getEditor().getOriginalEditor().getContribution('editor.contrib.folding');
var foldingContribModified = that2.$refs.editor.getEditor().getModifiedEditor().getContribution('editor.contrib.folding');
foldingContribModified.getFoldingModel().then(foldingModelModified => {
  foldingContrib.getFoldingModel().then(foldingModel => {
    foldingModel.onDidChange((e) => {
      var regions = foldingModel.regions;
      var regionsModified = foldingModelModified.regions;
	    let toToggle = [];
    	for (let i = regions.length - 1; i >= 0; i--) {
    	   if(regions.isCollapsed(i) != regionsModified.isCollapsed(i))
    	   {
    	   toToggle.push(regionsModified.toRegion(i));
    	   }
    	}
    	foldingModelModified.toggleCollapseState(toToggle);
    });

    foldingModelModified.onDidChange((e) => {
      var regions = foldingModel.regions;
      var regionsModified = foldingModelModified.regions;
	    let toToggle = [];
    	for (let i = regions.length - 1; i >= 0; i--) {
    	   if(regions.isCollapsed(i) != regionsModified.isCollapsed(i))
    	   {
    	   toToggle.push(regions.toRegion(i));
    	   }
    	}
    	foldingModel.toggleCollapseState(toToggle);
    });
  });
 });
setTimeout(function() {
that2.$refs.editor.getEditor().getOriginalEditor().trigger('fold', 'editor.foldAll');
}, 1000);

  },
  components: {
    MonacoEditor
  },
  computed: mapGetters({
    currentProject: 'currentProject',
    projectsVcs: 'projectsVcs',
    projectsIts: 'projectsIts',
    projectsMl: 'projectsMl'
  })
}
</script>

<style>
.editor {
  width: 100% !important;
  height: 800px;
}

.myLineDecoration {
	background: lightblue;
	width: 5px !important;
	margin-left: 3px;
}
.myLineDecoration2 {
	background: red;
	width: 5px !important;
	margin-left: 3px;
}
</style>
