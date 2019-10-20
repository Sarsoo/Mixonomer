import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js";
import BarChart from "./BarChart.js";

class Count extends Component {

    constructor(props){
        super(props);
        this.state = {
            playlists: [],
            isLoading: true
        }
        this.getPlaylists();
    }

    getPlaylists(){
        axios.get('/api/playlists')
        .then((response) => {

            var playlists = [];

            var playlist_in;
            for(playlist_in of response.data.playlists) {
                if(playlist_in['lastfm_stat_last_refresh'] != undefined){
                    playlists.push(playlist_in);
                }
            }

            playlists.sort(function(a, b){
                return b['lastfm_stat_count'] - a['lastfm_stat_count'];
            });

            this.setState({
                playlists: playlists,
                isLoading: false
            });
        })
        .catch((error) => {
            console.log(error);
            showMessage(`error getting playlists (${error.response.status})`);
        });
    }

    render() {

        var data = this.state.playlists.map((entry) => {
            return {
                "label": entry.name,
                "value": entry.lastfm_stat_count
            };
        })

        var table = <div>
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan='2'>
                            <h1 className="ui-text center-text text-no-select">scrobble counts</h1>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.playlists.map((entry) => <Row name={entry.name} count={entry.lastfm_stat_count} percent={entry.lastfm_stat_percent} key={entry.name}/>)}
                </tbody>
            </table>
            <BarChart data={data} title='scrobbles'/>
            </div>;

        const loadingMessage = <p className="center-text">loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

function Row(props){
    return <tr>
        <td className="ui-text center-text text-no-select" style={{width: '50%'}}>{props.name}</td>
        <td className="ui-text center-text text-no-select"><b>{props.count.toLocaleString()} / {props.percent}%</b></td>
    </tr>;
}

export default Count;