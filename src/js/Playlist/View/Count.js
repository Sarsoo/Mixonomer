import React, { Component } from "react";
import { ThemeProvider, Typography } from "@material-ui/core";
const axios = require('axios');

import showMessage from "../../Toast.js"
import GlobalTheme from "../../Theme";

const LazyPieChart = React.lazy(() => import("../../Maths/PieChart"))

export class Count extends Component {

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
                showMessage('No Stats For This Playlist');
            }
        })
        .catch((error) => {
            showMessage(`Error Getting Playlist Info (${error.response.status})`);
        });
    }

    updateStats(){
        axios.get(`/api/spotfm/playlist/refresh?name=${ this.state.name }`)
        .then((response) => {
            showMessage('Stats Refresh Queued');
        })
        .catch((error) => {
            if(error.response.status == 401){
                showMessage('Missing Either Spotify or Last.fm link');
            }else{
                showMessage(`Error Refreshing (${error.response.status})`);
            }
        });
    }

    render() {
        return (
            <tbody>
                <tr>
                    <td className="ui-text center-text text-no-select">Scrobble Count: <b>{this.state.playlist.lastfm_stat_count.toLocaleString()} / {this.state.playlist.lastfm_stat_percent}%</b></td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">Album Count: <b>{this.state.playlist.lastfm_stat_album_count.toLocaleString()} / {this.state.playlist.lastfm_stat_album_percent}%</b></td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">Artist Count: <b>{this.state.playlist.lastfm_stat_artist_count.toLocaleString()} / {this.state.playlist.lastfm_stat_artist_percent}%</b></td>
                </tr>
                <tr>
                    <td className="ui-text center-text text-no-select">Last Updated <b>{this.state.playlist.lastfm_stat_last_refresh.toLocaleString()}</b></td>
                </tr>
                <React.Suspense fallback={<LoadingMessage/>}>
                <tr>
                    <td>
                        <LazyPieChart data={[{
                                "label": `${this.state.playlist.name} Tracks`,
                                "value": this.state.playlist.lastfm_stat_percent
                            },{
                                "label": 'Other',
                                "value": 100 - this.state.playlist.lastfm_stat_percent
                            }]} 
                            title={this.state.playlist.name}/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <LazyPieChart data={[{
                                "label": `${this.state.playlist.name} Albums`,
                                "value": this.state.playlist.lastfm_stat_album_percent
                            },{
                                "label": 'Other',
                                "value": 100 - this.state.playlist.lastfm_stat_album_percent
                            }]} 
                            title={this.state.playlist.name}/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <LazyPieChart data={[{
                                "label": `${this.state.playlist.name} Artists`,
                                "value": this.state.playlist.lastfm_stat_artist_percent
                            },{
                                "label": 'Other',
                                "value": 100 - this.state.playlist.lastfm_stat_artist_percent
                            }]} 
                            title={this.state.playlist.name}/>
                    </td>
                </tr>
                <tr>
                    <td colSpan="2">
                        <button style={{width: "100%"}} className="button" onClick={this.updateStats}>Update</button>
                    </td>
                </tr>
                </React.Suspense>
            </tbody>
        );
    }
}

function LoadingMessage(props) {
    return <tr><td><ThemeProvider theme={GlobalTheme}><Typography variant="h5" component="h2" className="ui-text center-text">Loading...</Typography></ThemeProvider></td></tr>;
}