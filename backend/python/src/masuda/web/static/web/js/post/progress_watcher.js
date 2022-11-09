export default function ProgressWatcher() {
    this.intervalId = 0;
    this.count = 0;
    this.disabledButton = null;
    this.delete_post_ids = null;
    this.watch = async (progressElement, progressId) => {
        const url = progressElement.dataset.url;
        const res = await fetch(url + progressId + '/', {
            method: 'GET'
        });
        const data = await res.json();
        console.log(data);

        // delete posts (selective-delete)
        this.deleteSelectively(data);
        // write overview
        // const overviewArea = progressElement.getElementsByTagName('span');
        const overviewArea = progressElement.querySelector('span.overview');
        if (overviewArea) {
            overviewArea.innerHTML = data.overview;
        }
        const messageArea = progressElement.querySelector('div.message');
        if (messageArea) {
            messageArea.innerHTML = data.memo;
        }
        console.log(data.memo)
        // write the progress bar
        this.writeProgressBar(progressElement, data);
        this.count++;
        console.log(progressId, this.count);
    };

    this.deleteSelectively = (data) => {
        // delete posts (selective-delete)
        if (data.delete_posts) {
            if (!this.delete_post_ids) {
                this.delete_post_ids = data.delete_posts
            }
            // if a post is deleted, delete the corresponding row and make a new delete_post_ids array
            this.delete_post_ids = this.delete_post_ids.filter(delete_post_id => {
                if (!data.delete_posts.includes(delete_post_id)) {
                    const row = document.getElementById('row-' + delete_post_id);
                    // if the row exists in the current page
                    if (row) {
                        row.remove();
                    }
                    return false;
                }
                return true;
            });
        } else {
            // finally, delete remaining rows
            if (this.delete_post_ids) {
                this.delete_post_ids = this.delete_post_ids.filter(delete_post_id => {
                    const row = document.getElementById('row-' + delete_post_id);
                    // if the row exists in the current page
                    if (row) {
                        row.remove();
                    }
                    return false;
                });
            }
        }
    };

    this.writeProgressBar = (progressElement, data) => {
        // get rate
        let rate = 0;
        if (data.total) {
            rate = Math.round(data.processed / data.total * 100);
        }
        // write the progress bar
        const bar = progressElement.getElementsByClassName('progress-bar')[0];
        bar.setAttribute('aria-valuenow', rate);
        bar.setAttribute('style', 'width: ' + rate + '%;');
        bar.innerHTML = data.processed + ' / ' + data.total;
        // stop when the process has stopped
        const stopStatus = ['PROCESSED', 'ERROR', 'STOPPED'];
        if (stopStatus.includes(data.status_name)) {
            bar.classList.remove('progress-bar-animated');
            bar.classList.remove('progress-bar-striped');
            // stop watching
            clearInterval(this.intervalId);
            if (this.disabledButton) {
                this.disabledButton.removeAttribute('disabled')
            }
        }
    };
};