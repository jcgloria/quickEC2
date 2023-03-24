<script>
  import { notification } from "../stores";
  import env from "../env.json"

  export let inboundRules = [{ port: 22, source: "own" }];
  export let linuxType = "ubuntu";
  export let publicIp = false;
  export let instanceName = "";

  function handleAddRule() {
    inboundRules = [...inboundRules, { port: 0, source: "own" }];
  }
  function clearForm() {
    instanceName = "";
    inboundRules = [{ port: 22, source: "own" }];
    linuxType = "ubuntu";
    publicIp = false;
  }

  async function handleLaunch() {
    notification.update((n) => (n = { status: "process", message: "Launching instance..." }));
    const response = await fetch(env.API_BASE_URL + "/api/instances", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        instanceName: instanceName,
        inboundRules: inboundRules,
        linuxType: linuxType,
        publicIp: publicIp,
      }),
    });
    const data = await response.json();
    if (data.message) {
        notification.update((n) => (n = data));
    } else {
      notification.update((n) => (n = { status: "error", message: "An unknown error ocurred" }));
    }
    clearForm();
  }
</script>

<main>
  <!-- Button trigger modal -->
  <div class="modal-dialog modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h1 class="modal-title fs-5" id="exampleModalLabel">Launch Instance</h1>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
          aria-label="Close"
        />
      </div>
      <div class="modal-body">
        <form>
          <div class="mb-3">
            <label for="InstanceName" class="form-label">Name</label>
            <input
              autocomplete="off"
              type="text"
              class="form-control"
              id="InstanceName"
              placeholder="MyEC2"
              bind:value={instanceName}
            />
          </div>
          <div class="form-check form-switch">
            <label class="form-check-label" for="PublicIpCheck"
              >Assign Public IP</label
            >
            <input
              class="form-check-input"
              type="checkbox"
              role="switch"
              id="PublicIpCheck"
              bind:checked={publicIp}
            />
          </div>
          <br />
          <div class="mb-3">
            <p class="col-form-label">Linux Type</p>
            <input
              type="radio"
              value="ubuntu"
              bind:group={linuxType}
              class="btn-check"
              name="LinuxType"
              id="ubuntu"
              autocomplete="off"
              checked
            />
            <label class="btn btn-outline-primary" for="ubuntu">Ubuntu</label>
            <input
              type="radio"
              value="amazon"
              bind:group={linuxType}
              class="btn-check"
              name="LinuxType"
              id="amazon"
              autocomplete="off"
            />
            <label class="btn btn-outline-primary" for="amazon">Amazon</label>
          </div>
          <br />
          <table id="inboundRules" class="table table-striped">
            <thead>
              <tr>
                <th scope="col">Inbound Port</th>
                <th scope="col">Source</th>
              </tr>
            </thead>
            <tbody>
              {#each inboundRules as { port, source }}
                <tr>
                  <td
                    ><input
                      autocomplete="off"
                      bind:value={port}
                      type="number"
                      class="form-control"
                      id="InboundPort"
                      placeholder="TCP Port"
                    /></td
                  >
                  <td>
                    <select
                      bind:value={source}
                      class="form-select"
                      aria-label="Source"
                    >
                      <option value="own" selected>My Current IP</option>
                      <option value="vpc">My VPC</option>
                      <option value="public">Anywhere</option>
                    </select>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
          <button
            on:click={handleAddRule}
            type="button"
            class="btn btn-primary btn-sm">Add Rule</button
          >
        </form>
        <br />
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal">Cancel</button
          >
          <button
            on:click={handleLaunch}
            type="button"
            class="btn btn-primary"
            data-bs-dismiss="modal">Launch</button
          >
        </div>
      </div>
    </div>
  </div>
</main>
<style>
</style>
