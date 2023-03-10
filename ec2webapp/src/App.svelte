<script>
  import Modal from "./LaunchModal.svelte";
  import Notifications from "./Notifications.svelte";
  import ConnectModal from "./ConnectModal.svelte";
  import { notification } from "../stores.js";
  import env from "../env.json"
  
  export let instances = []; // list of instances shown in main table
  export let connectInstance = {}; // for connect modal
  export let statusColors = {
    // status - font color mapping
    pending: "DarkGrey",
    running: "DarkGreen",
    stopped: "DarkGrey",
    terminated: "Black",
    "shutting-down": "DarkRed",
    stopping: "DarkGrey",
  };
  export let spinnerStatus = ["pending", "shutting-down", "stopping"]; // show spinner for these statuses

  /*
  * Fetch instances via GET request
  */
  async function getInstances() {
    const response = await fetch(env.API_BASE_URL + "/api/instances");
    const data = await response.json();
    if (data.status == "success") {
      instances = data.message;
    }else if(data.message){
      notification.update((n) => (n = {"status": "error", "message": data.message}));
    }else{
      notification.update((n) => (n = {"status": "error", "message": "An unknown error occurred"}));
    }
  }
  /*
  * Configure Connect Modal with the respective instance that was clicked
  */
  function handleConnect(instance) {
    connectInstance = {
      name: instance.name,
      linuxType: instance.linuxType,
      publicIp: instance.publicIp,
    };
  }
  /*
  * Start or Stop an instance via PUT request
  */
  async function handleStartStop(instance, action) {
    let msg = action == "start" ? "Starting instance" : "Stopping instance";
    msg = msg + " " + instance.name + "...";
    notification.update((n) => (n = { status: "process", message: msg }));
    const response = await fetch(env.API_BASE_URL + "/api/instances", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        action: action,
        instanceId: instance.instanceId
      }),
    });
    const data = await response.json();
    if (data.message) {
      notification.update((n) => data);
    } else {
      notification.update((n) => (n = {"status": "error", "message": "An unknown error occurred"}));
    }
  }
  /*
  * Terminate an instance via DELETE request
  */
  async function handleTerminate(instance) {
    notification.update((n) => (n = { status: "process", message: "Deleting instance..." }));
    const response = await fetch(env.API_BASE_URL + "/api/instances", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        'instanceId': instance.instanceId,
        'instanceName': instance.name
      }),
    });
    const data = await response.json();
    console.log(data)
    if (data.message) {
      notification.update((n) => data);
    } else {
      notification.update((n) => (n = {"status": "error", "message": "An unknown error occurred"}));
    }
  }
  /*
  * TODO: Handle inbound rules
  */
  function handleInboundRules(instance) {
    console.log("inbound rules");
  }
  /*
  * Refresh button handler. Also clears the notification store
  */
function handleRefresh() {
    notification.update((n) => (n = {}));
    getInstances();
  }

handleRefresh(); // initial instance fetch

</script>

<main>
  <nav class="navbar bg-body-tertiary bg-dark" data-bs-theme="dark">
    <div class="container-fluid">
      <span class="navbar-brand mb-0 h1">Quick EC2</span>
      <div>
        <button class="btn btn-secondary" on:click={handleRefresh}>
          <i class="bi bi-arrow-counterclockwise" />
        </button>
        <button
          type="button"
          class="btn btn-primary"
          data-bs-toggle="modal"
          data-bs-target="#launchModal">
          Launch Instance
        </button>
      </div>
    </div>
  </nav>
  <Notifications on:refresh={getInstances} />
  <!-- Launch Instance Modal -->
  <div
    class="modal fade"
    id="launchModal"
    tabindex="-1"
    aria-labelledby="launchModalLabel"
    aria-hidden="true"
  >
    <Modal />
  </div>
  <div class="container">
    <br />
    <table class="table table-hover">
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Type</th>
          <th scope="col">Public Ip</th>
          <th scope="col">Private Ip</th>
          <th scope="col">Status</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        {#if instances.length == 0}
          <tr>
            <td colspan="6" class="text-center">No instances</td>
          </tr>
        {/if}
        {#each instances as instance}
          <tr>
            <th scope="row">{instance.name}</th>
            <td>{instance.linuxType}</td>
            <td>{instance.publicIp}</td>
            <td>{instance.privateIp}</td>
            <td style="font-weight:bold;color:{statusColors[instance.status]}">
              {instance.status}
              {#if spinnerStatus.includes(instance.status)}
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              {/if}
            </td>
            <td>
              <div class="dropdown">
                <i id="three-dots" class="bi bi-three-dots" data-bs-toggle="dropdown" />
                <ul class="dropdown-menu">
                  {#if instance.status == "running"}
                    <li>
                      <button
                        on:click={handleConnect(instance)}
                        type="button"
                        class="dropdown-item"
                        data-bs-toggle="modal"
                        data-bs-target="#connectModal"
                      >
                        Connect
                      </button>
                    </li>
                    <li><hr class="dropdown-divider" /></li>
                    <li>
                      <button
                        on:click={handleStartStop(instance,'stop')}
                        class="dropdown-item">Stop</button
                      >
                    </li>
                  {:else if instance.status == "stopped"}
                    <li>
                      <button
                        on:click={handleStartStop(instance,'start')}
                        class="dropdown-item">Start</button
                      >
                    </li>
                    <li><hr class="dropdown-divider" /></li>
                  {/if}
                  <li>
                    <button
                      on:click={handleTerminate(instance)}
                      class="dropdown-item">Terminate</button
                    >
                  </li>
                  <li>
                    <button
                      on:click={handleInboundRules(instance)}
                      class="dropdown-item">Inbound Rules</button
                    >
                  </li>
                </ul>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  <div
    class="modal fade"
    id="connectModal"
    tabindex="-1"
    aria-labelledby="connectModalLabel"
    aria-hidden="true"
  >
    <ConnectModal {...connectInstance} />
  </div>
</main>

<style>
  td,
  th {
    text-align: center;
  }
  #three-dots {
    cursor: pointer;
  }
  #three-dots:hover {
    box-shadow: 0 0 5px #ccc;
    border-radius: 5px;
    background-color: #ccc;
  }
</style>
