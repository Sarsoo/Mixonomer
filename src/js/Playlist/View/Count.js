import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../../Toast.js"

class Count extends Component {

    constructor(props){
        super(props);
        this.state = {
            name: props.name,
            lastfm_refresh: 'never',
            lastfm_percent: 0,
            count: 0,
            isLoading: true
        }
        this.getUserInfo();

        this.updateStats = this.updateStats.bind(this);
    }

    getUserInfo(){
        axios.get(`/api/playlist?name=${ this.state.name }`)
        .then((response) => {
            if(response.data.lastfm_stat_last_refresh != undefined){
                this.setState({
                    count: response.data.lastfm_stat_count,
                    lastfm_refresh: response.data.lastfm_stat_last_refresh,
                    lastfm_percent: response.data.lastfm_stat_percent,
                    isLoading: false
                })
            }else{
                showMessage('no stats for this playlist');
            }
        })
        .catch((error) => {
            showMessage(`error getting playlist info (${error.response.status})`);
        });
    }

    updateStats(){
        axios.get(`/api/spotfm/playlist/refresh?name=${ this.state.name }`)
        .then((response) => {
            showMessage('stats refresh queued');
        })
        .catch((error) => {
            if(error.response.status == 401){
                showMessage('missing either spotify or last.fm link');
            }else{
                showMessage(`error refreshing (${error.response.status})`);
            }
        });
    }

    render() {
        return (
            <tbody>
                <tr>
                    <td className="ui-text center-text text-no-select">scrobble count: <b>{this.state.count.toLocaleString()}</b></td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">that's <b>{this.state.lastfm_percent}%</b> of all scrobbles</td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">last updated <b>{this.state.lastfm_refresh.toLocaleString()}</b></td>
                </tr>
                <tr>
                    <td colSpan="2">
                        <button style={{width: "100%"}} className="button" onClick={this.updateStats}>update</button>
                    </td>
                </tr>
            </tbody>
        );
    }
}



export default Count;