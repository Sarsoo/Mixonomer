import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../../Toast.js"
import PieChart from "../../Maths/PieChart.js";

class Count extends Component {

    constructor(props){
        super(props);
        this.state = {
            playlist: {
                lastfm_stat_album_count: 0,
                lastfm_stat_artist_count: 0,
                lastfm_stat_count: 0,

                lastfm_stat_album_percent: 0,
                lastfm_stat_artist_percent: 0,
                lastfm_stat_percent: 0,

                lastfm_stat_last_refresh: ''
            },
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
                    playlist: response.data,
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
                    <td className="ui-text center-text text-no-select">scrobble count: <b>{this.state.playlist.lastfm_stat_count.toLocaleString()} / {this.state.playlist.lastfm_stat_percent}%</b></td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">album count: <b>{this.state.playlist.lastfm_stat_album_count.toLocaleString()} / {this.state.playlist.lastfm_stat_album_percent}%</b></td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">artist count: <b>{this.state.playlist.lastfm_stat_artist_count.toLocaleString()} / {this.state.playlist.lastfm_stat_artist_percent}%</b></td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">last updated <b>{this.state.playlist.lastfm_stat_last_refresh.toLocaleString()}</b></td>
                </tr>
                <tr>
                    <td>
                        <PieChart data={[{
                                "label": `${this.state.playlist.name} tracks`,
                                "value": this.state.playlist.lastfm_stat_percent
                            },{
                                "label": 'other',
                                "value": 100 - this.state.playlist.lastfm_stat_percent
                            }]} 
                            title={this.state.playlist.name}/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <PieChart data={[{
                                "label": `${this.state.playlist.name} albums`,
                                "value": this.state.playlist.lastfm_stat_album_percent
                            },{
                                "label": 'other',
                                "value": 100 - this.state.playlist.lastfm_stat_album_percent
                            }]} 
                            title={this.state.playlist.name}/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <PieChart data={[{
                                "label": `${this.state.playlist.name} artists`,
                                "value": this.state.playlist.lastfm_stat_artist_percent
                            },{
                                "label": 'other',
                                "value": 100 - this.state.playlist.lastfm_stat_artist_percent
                            }]} 
                            title={this.state.playlist.name}/>
                    </td>
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