import ProgressWatcher from './progress_watcher.js';

window.addEventListener('load', () => {
    // show alert
    const putInfoBadge = (alertElement) => {
        const infoArea = document.getElementById('info-area');
        const infoBadge = document.getElementById('info-badge');
        alertElement.addEventListener('closed.bs.alert', () => {
            if (infoArea.childElementCount == 0) {
                infoBadge.classList.add('d-none');
            }
        });
        alertElement.classList.remove('d-none');
        if (infoBadge.classList.contains('d-none')) {
            infoBadge.classList.remove('d-none');
        }
        // return alertElement;
    };
    const showMessage = (message, success = true) => {
        const infoArea = document.getElementById('info-area');
        const alertElement = document.getElementById(success ? 'as-skeleton' : 'ad-skeleton').cloneNode(true);
        alertElement.getElementsByTagName('span')[0].innerHTML = message;
        putInfoBadge(alertElement);
        infoArea.appendChild(alertElement);
    };

    const showProgress = (progressId, disabledButton = null) => {
        const infoArea = document.getElementById('info-area');
        const alertElement = document.getElementById('ap-skeleton').cloneNode(true);
        const watcher = new ProgressWatcher();
        watcher.intervalId = setInterval(() => {watcher.watch(alertElement, progressId)}, 1000);
        watcher.disabledButton = disabledButton;
        putInfoBadge(alertElement);
        infoArea.appendChild(alertElement);
    };

    // delete,space masuda,reload button
    document.querySelectorAll('.del-btn,.space-masuda-btn,.reload-btn').forEach(item => {
        item.addEventListener('click', event => {
            item.setAttribute('disabled', 'disabled');
            const form = document.getElementById('ud-form');
            const formData = new FormData(form);
            (async () => {
                const res = await fetch(item.dataset.url, {
                    method: 'POST',
                    body: formData
                }).catch(error => {
                    console.log(error);
                    showMessage(error, false);
                    return;
                });
                const data = await res.json();
                console.log(data);
                if (data.result == 'success') {
                    if (item.classList.contains('del-btn')) {
                        document.getElementById('row-' + item.dataset.id).remove();
                    } else if (item.classList.contains('space-masuda-btn')) {
                        const tr = document.getElementById('row-' + item.dataset.id)
                        tr.querySelector('.title').innerHTML = '';
                        tr.querySelector('.body').innerHTML = ' ';
                    } else if (item.classList.contains('reload-btn')) {
                        const tr = document.getElementById('row-' + item.dataset.id)
                        tr.querySelector('.title').innerHTML = data.title;
                        tr.querySelector('.body').innerHTML = data.body;
                        tr.querySelector('.bookmark_count').innerHTML = data.bookmark_count;
                        tr.querySelector('.response_count').innerHTML = data.response_count;
                    }
                    // console.log('success');
                    showMessage(data.message);
                } else {
                    showMessage(data.message, false);
                }
            })();
        }, { once: true })
    });


    // fetch button
    document.getElementById('fetch-btn').addEventListener('click', event => {
        event.target.setAttribute('disabled', 'disabled');
        event.preventDefault();
        const form = document.getElementById('fetch-form');
        const formData = new FormData(form);
        (async () => {
            const res = await fetch(form.action, {
                method: 'POST',
                body: formData
            }).catch(error => {
                console.log(error);
                showMessage(error, false);
                return;
            });
            const data = await res.json();
            console.log(data);
            if (data.progress_id) {
                showProgress(data.progress_id, event.target);
            } else {
                console.log(data);
                const errors = [];
                if (data.page_from) {
                    console.log(data.page_from[0].message);
                    errors.push('page_from: ' + data.page_from[0].message);
                }
                if (data.page_to) {
                    console.log(data.page_to[0].message);
                    errors.push('page_to: ' + data.page_to[0].message);
                }
                if (errors.length > 0) {
                    showMessage(errors.join("\n"), false)
                } else {
                    showMessage('Some problems occurred. See progresses page.', false)
                }
                event.target.removeAttribute('disabled');
            }
            // if (data.result == 'success') {
            //     // document.getElementById('row-' + item.dataset.id).remove()
            //     console.log('success');
            // }
        })();
    });

    // check or uncheck of deleting later
    const addEventListnerToCheckDeleteLater = (item, postId, action, checkDirectly = null, callback = null) => {
        item.addEventListener(action, event => {
            const form = document.getElementById('check-form');
            console.log(form.action)
            let checked = '';
            // from checkbox
            if (checkDirectly === null) {
                checked = item.checked ? '/1/' : '/0/';
            // set true/false directly
            } else {
                checked = checkDirectly ? '/1/' : '/0/';
            }
            const url = form.action + postId + '/check' + checked;
            (async () => {
                const res = await fetch(url, {
                    method: 'GET'
                }).catch(error => {
                    console.log(error);
                    return;
                });
                const data = await res.json();
                console.log(data);
                if (typeof callback == 'function') {
                    callback();
                }
            })();
        });
    };

    // check to delete
    document.querySelectorAll('input.del_ids').forEach(item => {
        addEventListnerToCheckDeleteLater(item, item.value, 'change');
        // item.addEventListener('change', event => {
        //     console.log(item.checked);
        //     const form = document.getElementById('check-form');
        //     console.log(form.action)
        //     const checked = item.checked ? '/1/' : '/0/';
        //     const url = form.action + item.value + '/check' + checked;
        //     (async () => {
        //         const res = await fetch(url, {
        //             method: 'GET'
        //         }).catch(error => {
        //             console.log(error);
        //             return;
        //         });
        //         const data = await res.json();
        //         console.log(data);
        //     })();
        // });
    });

    // uncheck-all button
    document.getElementById('uncheck-all-btn').addEventListener('click', event => {
        const form = document.getElementById('uncheck-all-form');
        const formData = new FormData(form);
        document.querySelectorAll('input:checked[name="del_ids"]').forEach(item => {
            item.checked = false;
        });
        (async () => {
            const res = await fetch(form.action, {
                method: 'POST',
                body: formData
            }).catch(error => {
                console.log(error);
                showMessage(error, false);
                return;
            });
            // const data = await res.json();
            // console.log(data);
            // if (data.progress_id) {
            //     showProgress(data.progress_id, event.target);
            // } else {
            //     console.log(data);
            //     showMessage('Some problems occurred. See progresses page.', false)
            //     event.target.removeAttribute('disabled');
            // }
        })();
    });

    // show deleteLaterModal
    document.getElementById('deleteLaterModal').addEventListener('show.bs.modal', event => {
        // make a list item
        const makeLi = (postId) => {
            const li = document.createElement('li');
            li.classList.add('list-group-item');
            li.id = 'delete-post-' + postId
            return li;
        };
        // make a link to masuda
        const makeA = (anondUrl, masudaId) => {
            const a = document.createElement('a');
            a.href = anondUrl + '/' + masudaId;
            a.target = '_blank';
            a.textContent = masudaId;
            return a;
        };
        // make a cancel mark
        const makeX = (postId) => {
            const x = document.createElement('a');
            x.role = 'button'
            x.classList.add('mr-1');
            x.title = '解除';
            // uncheck and remove the item from the list when clicked
            addEventListnerToCheckDeleteLater(x, postId, 'click', false, () => {
                const checkbox = document.getElementById('del_ids-' + postId);
                // if the checkbox exists in the current page
                if (checkbox) {
                    checkbox.checked = false;
                }
                document.getElementById('delete-post-' + postId).remove();

                const modal = document.getElementById('deleteLaterModal');
                const ul = modal.querySelector('.modal-body ul');
                if (ul.childNodes.length == 0) {
                    modal.querySelector('.modal-title').textContent = '削除対象がありません'
                    modal.querySelector('#deleteLaterModalExecute').style.display = 'none';
                }
            });
            const icon = document.createElement('i');
            icon.classList.add('bi-x-square');
            x.appendChild(icon)
            return x;
        };

        const url = event.target.dataset.url;
        (async () => {
            const res = await fetch(url, {
                method: 'GET'
            }).catch(error => {
                console.log(error);
                showMessage(error, false);
                return;
            });
            const data = await res.json();
            console.log(data);
            const len = data.result.length;
            // const urls = [];
            const ul = document.createElement('ul');
            ul.classList.add('list-group', 'list-group-flush');
            for (let i = 0; i < len; i++) {
                const post = data.result[i];

                const li = makeLi(post.id)
                const a = makeA(event.target.dataset.anondUrl, post.masuda_id);
                const x = makeX(post.id);
                // x.addEventListener('click', event => {
                //     const form = document.getElementById('check-form');
                //     const url = form.action + post.id + '/check/0/';
                //     (async () => {
                //         const res = await fetch(url, {
                //             method: 'GET'
                //         }).catch(error => {
                //             return;
                //         });
                //         const data = await res.json();
                //         console.log(data);
                //         document.getElementById('del_ids-' + post.id).checked = false;
                //         document.getElementById('delete-post-' + post.id).remove();
                //     })();
                // });
                li.appendChild(x);
                li.appendChild(document.createTextNode(' '));
                li.appendChild(a);
                li.appendChild(document.createTextNode(' ' + post.title + ' B:' + post.bookmark_count));
                ul.appendChild(li)
                // urls[i] = '<p><a href="' + url + '" target="_blank">' + masuda_id + '</a> ' + post.title + ' B:' + post.bookmark_count + '</p>'
            }
            // const content = urls.join('');
            document.getElementById('deleteLaterModal').querySelector('.modal-body').textContent = '';
            if (len > 0) {
                event.target.querySelector('.modal-title').textContent = '以下の記事を削除します';
                event.target.querySelector('#deleteLaterModalExecute').style.display = 'inline';
                document.getElementById('deleteLaterModal').querySelector('.modal-body').appendChild(ul);
            } else {
                event.target.querySelector('.modal-title').textContent = '削除対象がありません'
                event.target.querySelector('#deleteLaterModalExecute').style.display = 'none';
            }

        })();
    });

    // selective delete button
    document.getElementById('deleteLaterModalExecute').addEventListener('click', event => {
        event.target.setAttribute('disabled', 'disabled');
        const form = document.getElementById('selective-delete-form');
        const formData = new FormData(form);
        // document.querySelectorAll('input:checked[name="del_ids"]').forEach(item => {
        //     formData.append(item.name, item.value)
        // });
        // console.log(formData);
        (async () => {
            const res = await fetch(form.action, {
                method: 'POST',
                body: formData
            }).catch(error => {
                console.log(error);
                showMessage(error, false);
                return;
            });
            const data = await res.json();
            console.log(data);
            if (data.progress_id) {
                showProgress(data.progress_id, event.target);
            } else {
                console.log(data);
                let error = 'Some problems occurred. See progresses page.';
                if (data.message) {
                    error = data.message;
                }
                showMessage(error, false)
                event.target.removeAttribute('disabled');
            }
        })();
    });
});