<script>
    import { notification } from "../stores";
    import env from "../env.json"
    import { createEventDispatcher } from "svelte";

    const eventSource = new EventSource(env.API_BASE_URL + "/stream");
    const dispatcher = createEventDispatcher();
    export let displayedAlert = {};
    displayedAlert = {}
    
    notification.subscribe((n) => {
            displayedAlert = n;     
    });

    eventSource.onmessage = (event) => {
        let data = JSON.parse(event.data);
        displayedAlert = data
        dispatcher("refresh");
    };
    function getAlertBox(status) {
        switch (status) {
            case "process":
                return "primary";
            case "success":
                return "success";
            case "error":
                return "danger";
            default:
                return "primary";
        }
    }
</script>

<main>
    {#if displayedAlert.message}
        <br />
        <div class="alert alert-{getAlertBox(displayedAlert.status)}" role="alert">
            {displayedAlert.message}
                {#if displayedAlert.status == "process"}
            <div class="spinner-border float-end" role="status">
                    <span class="visually-hidden">Loading...</span>
            </div>
            {/if} 
        </div>
    {/if}
</main>

<style>
    .alert {
        max-width: 1200px;
        margin: 0 auto;
    }
</style>
