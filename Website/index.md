
# Generate code plugs for your radio

This page allows you to select from one of several sources or to
upload your own. It can generate CSV files for Chirp, RT Systems
(tested with Yaesu FT-60 and several other radios), Icom, or Anytone.

You can filter the input based on various criteria and slightly
customize the output.

<html><p>Click <a href="help.html" target="CodePlugHelp">here for detailed instructions</a></p></html>

<html>
<form action="./cgi-bin/generate.cgi" method=POST enctype="multipart/form-data" name="mainForm">
<h2>Select source:</h2>
<p><label for="source">Source:</label> <select id="source" name="source" onchange="inputSelection()">
<!-- NOTE: edit the javascript if you change this list -->
[for sources]<option>[sources]</option>
[end]
<option>Upload …</option> <!-- Note the index of this item -->
</select>
</p>

<div id="drop-area" class="drop-area" hidden=true>
  <p>Drag & drop file here or click to select</p>
  <input type="file" id="fileInput" name="fileInput">
  <p>See <a href="help.html#accepted-formats" target="CodePlugHelp" id="drop-help">Accepted Formats</a> for information.</p>
</div>

<p class="filters"><label for="bandFilter">Filter by band:</label> <input type=checkbox id=bandFilter name="bandFilter" onclick="bandFilterVisibility()">&nbsp;
<span id="bandFilterChecks" style="visibility: hidden">
<label for="hf">HF</label><input type=checkbox id="hf" name="hf">&nbsp;
<label for="vhf">2m</label><input type=checkbox id="vhf" name="vhf">&nbsp;
<label for="vhf2">1.25m</label><input type=checkbox id="vhf2" name="vhf2">&nbsp;
<label for="uhf">70cm</label><input type=checkbox id="uhf" name="uhf">&nbsp;
<label for="gmrs">GMRS</label><input type=checkbox id="gmrs" name="gmrs">&nbsp;
<label for="digital">Digital</label><input type=checkbox id="digital" name="digital">
</span>
</p>

<p class="filters"><label for="modeFilter">Filter by mode:</label> <input type=checkbox id=modeFilter name="modeFilter" onclick="modeFilterVisibility()">&nbsp;
<span id="modeFilterChecks" style="visibility: hidden">
<label for="FM">FM</label><input type=checkbox id="FM" name="FM">&nbsp;
<label for="AM">AM</label><input type=checkbox id="AM" name="AM">&nbsp;
<label for="LSB">LSB</label><input type=checkbox id="LSB" name="LSB">&nbsp;
<label for="USB">USB</label><input type=checkbox id="USB" name="USB">&nbsp;
<label for="CW">CW</label><input type=checkbox id="CW" name="CW">&nbsp;
<label for="PKT">PKT</label><input type=checkbox id="PKT" name="PKT">&nbsp;
<label for="P25">P25</label><input type=checkbox id="P25" name="P25">&nbsp;
<label for="DMR">DMR</label><input type=checkbox id="DMR" name="DMR">&nbsp;
<label for="DSTAR">DSTAR</label><input type=checkbox id="DSTAR" name="DSTAR">&nbsp;
<label for="NXDN">NXDN</label><input type=checkbox id="NXDN" name="NXDN">&nbsp;
<label for="ATV">ATV</label><input type=checkbox id="ATV" name="ATV">&nbsp;
<label for="DATV">DATV</label><input type=checkbox id="DATV" name="DATV">&nbsp;
<label for="DIG">Other digital</label><input type=checkbox id="DIG" name="DIG">&nbsp;
</span>
</p>

<h2>Output options:</h2>
<p><label for="outputFormat">Format: </label><select id="outputFormat" name="outputFormat">
<option>Chirp</option>
<option>RT Systems</option>
<option>Icom</option>
<option>Anytone</option>
</select>
</p>
<p><label for="start">Start: </label><input type=text value="1" size=5 id="start" name="start"></p>

<p><label for="longNames">Long names: </label>
<input type=checkbox id="longNames" name="longNames">
<button id="nameQ" popovertarget="nameHelp" type="button" class="circleBtn">?</button></p>
<div id=nameHelp popover class="popupBox">
<p>By default, the name field in the output
is the same as the name field in the input, which is usually short enough to
fit the display of most radios.</p>
<p>Some radios can display longer names, and so this flag adds some extra
information to the name where appropriate. Typically this means adding the
station call sign if not already part of the name. For e.g. ICS 217 forms,
the channel number is added if not already present.</p>
</div>

<p><label for="sparse">Sparse: </label><input type=checkbox id="sparse" name="sparse">
<button id="sparseQ" popovertarget="sparseHelp" type="button" class="circleBtn">?</button></p>

<div id="sparseHelp" popover class="popupBox">
<p>By default, output records are written and numbered in the order
they're read from the input. The record numbers start at the Start
value given above and are strictly incrementing, ignoring the record
numbers in the input file.</p>
<p>Gaps in the input record numbers do not result in gaps in the
output. The output might look something like this:</p>
<table>
<tr><th>Location</th><th>Name</th><th>Frequency</th></tr>
<tr><td>1</td><td>Chan 1</td><td>146.96</td></tr>
<tr><td>2</td><td>Chan 2</td><td>146.96</td></tr>
<tr><td>3</td><td>Chan 3</td><td>146.40</td></tr>
<tr><td>4</td><td>Chan 6</td><td>146.50</td></tr>
<tr><td>5</td><td>Chan 7</td><td>146.60</td></tr>
</table>
<p>When <b>Sparse</b> is selected, the input record numbers are taken into account,
and if there are gaps in the input, there will be gaps in the output.</p>
<table>
<tr><th>Location</th><th>Name</th><th>Frequency</th></tr>
<tr><td>1</td><td>Chan 1</td><td>146.96</td></tr>
<tr><td>2</td><td>Chan 2</td><td>146.96</td></tr>
<tr><td>3</td><td>Chan 3</td><td>146.40</td></tr>
<tr><td><b>6</b></td><td>Chan 6</td><td>146.50</td></tr>
<tr><td><b>7</b></td><td>Chan 7</td><td>146.60</td></tr>
</table>
<p>If the input file does not have channel numbers, this option has no effect.</p>
<p>For more details, see
<a href="help.html#sparse" target="CodePlugHelp">help file</a></p>
</div>

</p>
<p><label for="skip">Skip: </label><input type=checkbox id="skip" name="skip">
<button id="skipQ" popovertarget="skipHelp" type="button" class="circleBtn">?</button></p>
<div id="skipHelp" popover class="popupBox">
<p>Sets the "skip this channel while scanning" flag for all channels. If the
input CSV file had a "skip" column, it is overridden.</p></div>

<p><input type=submit name="submit"></p>
</form>
<div id="debug"></div>
</html>

<html>
<script language="JavaScript">
<!--
setupDnD();
setupPopover("nameQ","nameHelp");
setupPopover("sparseQ","sparseHelp");
setupPopover("skipQ","skipHelp");
-->
</script>
