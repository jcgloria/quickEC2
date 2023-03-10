<script>
  import env from "../env.json";

  export let toastMessage = "Copied to clipboard!";
  export let name = "";
  export let linuxType = "";
  export let publicIp = "";
  export let key_path = "private_key.pem";
  $: user = linuxType == "ubuntu" ? "ubuntu" : "ec2-user";
  $: connect_string = "ssh -i" + " " + key_path + " " + user + "@" + publicIp;

  function handleCopyClipboard() {
    navigator.clipboard.writeText(connect_string);
    const toast = new bootstrap.Toast(document.getElementById("liveToast"));
    toast.show();
  }
  async function get_key() {
    const fetch_path = await fetch(env.API_BASE_URL + "/api/key_path");
    const data = await fetch_path.json();
    if (data.status == "success") {
      key_path = data.message;
    }
  }
  get_key();
</script>

<main>
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h1 class="modal-title fs-5" id="connectModalLabel">
          Connect to Instance {name}
        </h1>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
          aria-label="Close"
        />
      </div>
      <div class="modal-body">
        {#if publicIp}
          <div class="input-group mb-3">
            <input
              bind:value={connect_string}
              type="text"
              class="form-control"
              disabled
            />
            <button
              on:click={handleCopyClipboard}
              data-bs-toggle="tooltip"
              data-bs-placement="top"
              data-bs-title="Copy to Clipboard"
              class="btn btn-outline-secondary"
              type="button"
            >
              <i class="bi-clipboard" />
            </button>
          </div>
        {:else}
          <p>Instance does not have a public IP exposed</p>
        {/if}
      </div>
    </div>
  </div>
  <!-- Toast -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div
      id="liveToast"
      class="toast align-items-center text-bg-secondary border-0"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">{toastMessage}</div>
        <button
          type="button"
          class="btn-close btn-close-white me-2 m-auto"
          data-bs-dismiss="toast"
          aria-label="Close"
        />
      </div>
    </div>
  </div>
</main>

<style>
</style>
