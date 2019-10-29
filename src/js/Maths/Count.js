import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js";
import BarChart from "./BarChart.js";
import PieChart from "./PieChart.js";

class Count extends Component {

    constructor(props){
        super(props);
        this.state = {
            playlists: [],
            isLoading: true,

            chartPlaylists: []
        }
        this.getPlaylists();

        this.handleCheckbox = this.handleCheckbox.bind(this);
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

    handleCheckbox(event) {
        if(event.target.checked == true){
            var playlists = this.state.chartPlaylists.slice();
            playlists.push(event.target.name);

            this.setState({chartPlaylists: playlists});
        }else{
            var playlists = this.state.chartPlaylists.slice();
            playlists.splice(playlists.indexOf(event.target.name), 1);

            this.setState({chartPlaylists: playlists});
        }
    }

    getPieChartTrackData(){
        var playlists = this.state.chartPlaylists;

        if(playlists.length > 0){

            var data = playlists.map((entry) => {
                
                var i;
                for(i = 0; i < this.state.playlists.length; i++){
                    var playlist = this.state.playlists[i];
                    if(playlist.name == entry){

                        return {
                            "label": playlist.name,
                            "value": playlist.lastfm_stat_percent
                        }
                    }
                }

                console.log(`${entry} not found`);
            });

            var total = data.reduce((total, value) => {
                return total + value.value;
            }, 0);

            data.sort((a, b) => {
                if(a.value > b.value) { return -1; }
                if(a.value < b.value) { return 1; }
                return 0;
            })

            if(total > 100){
                return [{
                    'label': 'over 100%',
                    'value': 100
                }];
            }else{
                data.push({
                    'label': 'other',
                    'value': 100 - total
                })
            }
            return data;
        }else{
            return [{
                'label': 'no selection',
                'value': 100
            }];
        }
    }

    getPieChartAlbumData(){
        var playlists = this.state.chartPlaylists;

        if(playlists.length > 0){

            var data = playlists.map((entry) => {
                
                var i;
                for(i = 0; i < this.state.playlists.length; i++){
                    var playlist = this.state.playlists[i];
                    if(playlist.name == entry){

                        return {
                            "label": playlist.name,
                            "value": playlist.lastfm_stat_album_percent
                        }
                    }
                }

                console.log(`${entry} not found`);
            });

            var total = data.reduce((total, value) => {
                return total + value.value;
            }, 0);

            data.sort((a, b) => {
                if(a.value > b.value) { return -1; }
                if(a.value < b.value) { return 1; }
                return 0;
            })

            if(total > 100){
                return [{
                    'label': 'over 100%',
                    'value': 100
                }];
            }else{
                data.push({
                    'label': 'other',
                    'value': 100 - total
                })
            }
            return data;
        }else{
            return [{
                'label': 'no selection',
                'value': 100
            }];
        }
    }

    getPieChartArtistData(){
        var playlists = this.state.chartPlaylists;

        if(playlists.length > 0){

            var data = playlists.map((entry) => {
                
                var i;
                for(i = 0; i < this.state.playlists.length; i++){
                    var playlist = this.state.playlists[i];
                    if(playlist.name == entry){

                        return {
                            "label": playlist.name,
                            "value": playlist.lastfm_stat_artist_percent
                        }
                    }
                }

                console.log(`${entry} not found`);
            });

            var total = data.reduce((total, value) => {
                return total + value.value;
            }, 0);

            data.sort((a, b) => {
                if(a.value > b.value) { return -1; }
                if(a.value < b.value) { return 1; }
                return 0;
            })

            if(total > 100){
                return [{
                    'label': 'over 100%',
                    'value': 100
                }];
            }else{
                data.push({
                    'label': 'other',
                    'value': 100 - total
                })
            }
            return data;
        }else{
            return [{
                'label': 'no selection',
                'value': 100
            }];
        }
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
                        <th colSpan='3'>
                            <h1 className="ui-text center-text text-no-select">scrobble counts</h1>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.playlists.map((entry) => <Row name={entry.name} count={entry.lastfm_stat_count} percent={entry.lastfm_stat_percent} handler={this.handleCheckbox} key={entry.name}/>)}
                </tbody>
            </table>
            <BarChart data={data} title='scrobbles'/>

            <PieChart data={this.getPieChartTrackData()} title='genres'/>
            <PieChart data={this.getPieChartAlbumData()} title='genres'/>
            <PieChart data={this.getPieChartArtistData()} title='genres'/>

            </div>;

        const loadingMessage = <p className="center-text">loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

function Row(props){
    return <tr>
        <td className="ui-text center-text text-no-select" style={{width: '50%'}}>{props.name}</td>
        <td className="ui-text center-text text-no-select"><b>{props.count.toLocaleString()} / {props.percent}%</b></td>
        <td className="ui-text center-text text-no-select" style={{width: '20px'}}><input type="checkbox" name={props.name} onChange={props.handler} /></td>
    </tr>;
}

export default Count;