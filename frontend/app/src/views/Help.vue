<template>
  <div class="wrapper">
    <div class="animated fadeIn">
      <div class="card">
        <div class="card-header">
          <i class="fa fa-question"></i> Help
        </div>
        <div class="card-block">
          <strong>Generic Information</strong>
          <p>
            VisualSHARK is a frontend for the MongoDB of the SmartSHARK software repository mining ecosystem.
          </p>

          <strong>Labeling Information</strong>
          <p>
            The commits/lines that should be labeled are randomly drawn from all available, manually validated issues for the project that is selected on the right side.
          </p>
          <p>
          <strong>Description of labels</strong><br/>
          <ol>
            <li>Bugfix: The line contributes to the corrective change that is performed to address the issue that is described.</li>
            <li>Whitespace: The line only contains changes to whitespaces that do not affect the logic of the source code.</li>
            <li>Documentation: The line only contains changes to documentation of the software, including line comments or documentation files.</li>
            <li>Refactoring: The change is a refactoring, e.g., a renaming of a variable or the extraction of a method.</li>
            <li>Test: The change is only to tests of the project, e.g., test code or test data.</li>
            <li>Unrelated: The change is neither of the above, e.g., the addition of features unrelated to the described issue.</li>
          </ol>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'help',
}
</script>
<style>
</style>
