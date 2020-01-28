import React, { Component } from "react";
const axios = require('axios');

import { Card, Paper, Button, CircularProgress, FormControl, TextField, Input, InputLabel, Select, Checkbox, FormControlLabel, IconButton, InputAdornment } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { Add, Delete } from '@material-ui/icons';
import GlobalTheme from "../../Theme.js" 

import showMessage from "../../Toast.js";

var thisMonth = [
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'septempber',
    'october',
    'november',
    'december'
];

var lastMonth = [
    'december',
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'septempber',
    'october',
    'november'
];

export class Edit extends Component{

    constructor(props){
        super(props);
        this.state = {
            name: this.props.name,
            parts: [],
            playlists: [],
            filteredPlaylists: [],
            playlist_references: [],
            type: 'default',

            chart_limit: '',
            chart_range: '',

            day_boundary: '',
            recommendation_sample: '',
            newPlaylistName: '',
            newReferenceName: '',

            shuffle: false,
            include_recommendations: false,
            add_this_month: false,
            add_last_month: false,

            isLoading: true
        }
        this.handleAddPart = this.handleAddPart.bind(this);
        this.handleAddReference = this.handleAddReference.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleRemovePart = this.handleRemovePart.bind(this);
        this.handleRemoveReference = this.handleRemoveReference.bind(this);

        this.handleRun = this.handleRun.bind(this);

        this.handleShuffleChange = this.handleShuffleChange.bind(this);

        this.handleIncludeLibraryTracksChange = this.handleIncludeLibraryTracksChange.bind(this);

        this.handleIncludeRecommendationsChange = this.handleIncludeRecommendationsChange.bind(this);
        this.handleThisMonthChange = this.handleThisMonthChange.bind(this);
        this.handleLastMonthChange = this.handleLastMonthChange.bind(this);

        this.handleChartLimitChange = this.handleChartLimitChange.bind(this);
        this.handleChartRangeChange = this.handleChartRangeChange.bind(this);
    }

    componentDidMount(){
        axios.all([this.getPlaylistInfo(), this.getPlaylists()])
        .then(axios.spread((info, playlists) => {
            
            info.data.parts.sort(function(a, b){
                if(a.toLowerCase() < b.toLowerCase()) { return -1; }
                if(a.toLowerCase() > b.toLowerCase()) { return 1; }
                return 0;
            });

            info.data.playlist_references.sort(function(a, b){
                if(a.toLowerCase() < b.toLowerCase()) { return -1; }
                if(a.toLowerCase() > b.toLowerCase()) { return 1; }
                return 0;
            });

            var filteredPlaylists = playlists.data.playlists.filter((entry) => entry.name != this.state.name);

            this.setState(info.data);
            this.setState({
                playlists: playlists.data.playlists,
                newReferenceName: filteredPlaylists.length > 0 ? filteredPlaylists[0].name : '',
                isLoading: false
            });
        }))
        .catch((error) => {
            showMessage(`Error Getting Playlist Info (${error.response.status})`);
        });
    }

    getPlaylistInfo(){
        return axios.get(`/api/playlist?name=${ this.state.name }`);
    }

    getPlaylists(){
        return axios.get(`/api/playlists`);
    }

    handleInputChange(event){
        
        this.setState({
            [event.target.name]: event.target.value
        });

        if(event.target.name == 'day_boundary'){
            this.handleDayBoundaryChange(event.target.value);
        }
        if(event.target.name == 'recommendation_sample'){
            this.handleRecommendationsSampleChange(event.target.value);
        }
        if(event.target.name == 'type'){
            this.handleTypeChange(event.target.value);
        }
        if(event.target.name == 'chart_range'){
            this.handleChartRangeChange(event.target.value);
        }
        if(event.target.name == 'chart_limit'){
            this.handleChartLimitChange(event.target.value);
        }
    }

    handleDayBoundaryChange(boundary) {
        if(boundary == ''){
            boundary = 0;
            this.setState({
                day_boundary: 0
            });
        }
        axios.post('/api/playlist', {
            name: this.state.name,
            day_boundary: parseInt(boundary)
        }).catch((error) => {
            showMessage(`Error Updating Boundary Value (${error.response.status})`);
        });
    }

    handleRecommendationsSampleChange(sample){
        if(sample == ''){
            sample = 0;
            this.setState({
                recommendation_sample: 0
            });
        }
        axios.post('/api/playlist', {
            name: this.state.name,
            recommendation_sample: parseInt(sample)
        }).catch((error) => {
            showMessage(`Error Updating Rec. Sample Value (${error.response.status})`);
        });
    }

    handleTypeChange(sample){
        axios.post('/api/playlist', {
            name: this.state.name,
            type: sample
        }).catch((error) => {
            showMessage(`Error Updating Type (${error.response.status})`);
        });
    }

    handleShuffleChange(event) {
        this.setState({
            shuffle: event.target.checked
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            shuffle: event.target.checked
        }).catch((error) => {
            showMessage(`Error Updating Shuffle Value (${error.response.status})`);
        });
    }

    handleThisMonthChange(event) {
        this.setState({
            add_this_month: event.target.checked
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            add_this_month: event.target.checked
        }).catch((error) => {
            showMessage(`Error Updating Add This Month (${error.response.status})`);
        });
    }

    handleLastMonthChange(event) {
        this.setState({
            add_last_month: event.target.checked
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            add_last_month: event.target.checked
        }).catch((error) => {
            showMessage(`Error Updating Add Last Month (${error.response.status})`);
        });
    }

    handleIncludeRecommendationsChange(event) {
        this.setState({
            include_recommendations: event.target.checked
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            include_recommendations: event.target.checked
        }).catch((error) => {
            showMessage(`Error Updating Rec. Value (${error.response.status})`);
        });
    }

    handleIncludeLibraryTracksChange(event) {
        this.setState({
            include_library_tracks: event.target.checked
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            include_library_tracks: event.target.checked
        }).catch((error) => {
            showMessage(`Error Updating Library Tracks (${error.response.status})`);
        });
    }

    handleChartRangeChange(value) {
        axios.post('/api/playlist', {
            name: this.state.name,
            chart_range: value
        }).catch((error) => {
            showMessage(`Error Updating Chart Range (${error.response.status})`);
        });
    }

    handleChartLimitChange(value) {
        axios.post('/api/playlist', {
            name: this.state.name,
            chart_limit: parseInt(value)
        }).catch((error) => {
            showMessage(`Error Updating Limit (${error.response.status})`);
        });
    }

    handleAddPart(event){
        
        if(this.state.newPlaylistName.length != 0){

            var check = this.state.parts.includes(this.state.newPlaylistName);

            if(check == false) {
                var parts = this.state.parts.slice();
                parts.push(this.state.newPlaylistName);

                parts.sort(function(a, b){
                    if(a.toLowerCase() < b.toLowerCase()) { return -1; }
                    if(a.toLowerCase() > b.toLowerCase()) { return 1; }
                    return 0;
                });

                this.setState({
                    parts: parts,
                    newPlaylistName: ''
                });
                axios.post('/api/playlist', {
                    name: this.state.name,
                    parts: parts
                }).catch((error) => {
                    showMessage(`Error Adding Part (${error.response.status})`);
                });
            }else{
                showMessage('Playlist Already Added');  
            }

        }else{
            showMessage('Enter Playlist Name');
        }
    }

    handleAddReference(event){

        if(this.state.newReferenceName.length != 0){
            
            var check = this.state.playlist_references.includes(this.state.newReferenceName);

            if(check == false) {
                var playlist_references = this.state.playlist_references.slice();
                playlist_references.push(this.state.newReferenceName);
                
                playlist_references.sort(function(a, b){
                    if(a.toLowerCase() < b.toLowerCase()) { return -1; }
                    if(a.toLowerCase() > b.toLowerCase()) { return 1; }
                    return 0;
                });

                var filteredPlaylists = this.state.playlists.filter((entry) => entry.name != this.state.name);
                
                this.setState({
                    playlist_references: playlist_references,
                    newReferenceName: filteredPlaylists.length > 0 ? filteredPlaylists[0].name : ''
                });
                axios.post('/api/playlist', {
                    name: this.state.name,
                    playlist_references: playlist_references
                }).catch((error) => {
                    showMessage(`Error Adding Reference (${error.response.status})`);
                });

            }else{
                showMessage('Playlist Already Added');  
            }

        }else{
            showMessage('No Other Playlists to Add');   
        }
    }

    handleRemovePart(id, event){
        var parts = this.state.parts;
        parts = parts.filter(e => e !== id);
        this.setState({
            parts: parts
        });

        if(parts.length == 0) {
            parts = -1;
        }

        axios.post('/api/playlist', {
            name: this.state.name,
            parts: parts
        }).catch((error) => {
            showMessage(`Error Removing Part (${error.response.status})`);
        });
    }

    handleRemoveReference(id, event){
        var playlist_references = this.state.playlist_references;
        playlist_references = playlist_references.filter(e => e !== id);
        this.setState({
            playlist_references: playlist_references
        });

        if(playlist_references.length == 0) {
            playlist_references = -1;
        }

        axios.post('/api/playlist', {
            name: this.state.name,
            playlist_references: playlist_references
        }).catch((error) => {
            showMessage(`Error Removing Reference (${error.response.status})`);
        });
    }

    handleRun(event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.spotify_linked == true){
                axios.get('/api/playlist/run', {params: {name: this.state.name}})
                .then((reponse) => {
                    showMessage(`${this.state.name} Run`);
                })
                .catch((error) => {
                    showMessage(`Error Running ${this.state.name} (${error.response.status})`);
                });
            }else{
                showMessage(`Link Spotify Before Running`);
            }
        }).catch((error) => {
            showMessage(`Error Running ${this.state.name} (${error.response.status})`);
        });
    }

    render(){

        var date = new Date();

        const table = (
            <ThemeProvider theme={GlobalTheme}>
            <Card>
                { this.state.playlist_references.length > 0 && <tr><td colSpan="2" className="ui-text center-text text-no-select" style={{fontStyle: 'italic'}}>Managed</td></tr> }
                { this.state.playlist_references.length > 0 && <ListBlock handler={this.handleRemoveReference} list={this.state.playlist_references}/> }

                { this.state.parts.length > 0 && <tr><td colSpan="2" className="ui-text center-text text-no-select" style={{fontStyle: 'italic'}}>Spotify</td></tr> }
                { this.state.parts.length > 0 && <ListBlock handler={this.handleRemovePart} list={this.state.parts}/> }
                <tr>
                    <td colSpan="2" className="center-text ui-text text-no-select" style={{fontStyle: "italic"}}>
                        <br></br>Spotify playlist can be the name of either your own created playlist or one you follow, names are case sensitive
                    </td>
                </tr>
                <FormControl>
                    <InputLabel htmlFor="newPlaylistName">Spotify Playlist</InputLabel>
                    <Input
                        id="newPlaylistName"
                        name="newPlaylistName"
                        type="text"
                        value={this.state.newPlaylistName}
                        onChange={this.handleInputChange}
                        endAdornment={
                        <InputAdornment position="end">
                            <IconButton onClick={this.handleAddPart} >
                                <Add/>
                            </IconButton>
                        </InputAdornment>
                        }
                    />
                </FormControl>
                <tr>
                    <td>
                        <FormControl variant="filled">
                            <InputLabel htmlFor="chart_range">Managed Playlist</InputLabel>
                            <Select
                            native
                            value={this.state.newReferenceName}
                            onChange={this.handleInputChange}
                            inputProps={{
                                name: "newReferenceName",
                                id: "newReferenceName",
                            }}
                            >
                            { this.state.playlists
                                .filter((entry) => entry.name != this.state.name)
                                .map((entry) => <ReferenceEntry name={entry.name} key={entry.name} />) }
                            </Select>
                        </FormControl>
                    </td>
                    <td>
                        <Button className="full-width" onClick={this.handleAddReference}>Add</Button>
                    </td>
                </tr>
                <FormControlLabel
                    control={
                    <Checkbox checked={this.state.shuffle} onChange={this.handleShuffleChange} />
                    }
                    labelPlacement="bottom"
                    label="Shuffle"/>
                <FormControlLabel
                    control={
                    <Checkbox checked={this.state.include_recommendations} onChange={this.handleIncludeRecommendationsChange} />
                    }
                    labelPlacement="bottom"
                    label="Recommendations"/>
                <FormControlLabel
                    control={
                    <Checkbox checked={this.state.include_library_tracks} onChange={this.handleIncludeLibraryTracksChange} />
                    }
                    labelPlacement="bottom"
                    label="Library Tracks"/>
                <TextField type="number" 
                        name="recommendation_sample"
                        // className="full-width"
                        label="Recommendation Size"
                        value={this.state.recommendation_sample}
                        onChange={this.handleInputChange}></TextField>

                { this.state.type == 'fmchart' &&
                    <TextField type="number" 
                        name="chart_limit"
                        // className="full-width"
                        label="Chart Size"
                        value={this.state.chart_limit}
                        onChange={this.handleInputChange}></TextField>
                }
                { this.state.type == 'fmchart' &&
                    <FormControl variant="filled">
                        <InputLabel htmlFor="chart_range">Chart Range</InputLabel>
                        <Select
                        native
                        value={this.state.chart_range}
                        onChange={this.handleInputChange}
                        inputProps={{
                            name: "chart_range",
                            id: "chart_range",
                        }}
                        >
                            <option value="WEEK">7 Day</option>
                            <option value="MONTH">30 Day</option>
                            <option value="QUARTER">90 Day</option>
                            <option value="HALFYEAR">180 Day</option>
                            <option value="YEAR">365 Day</option>
                            <option value="OVERALL">Overall</option>
                            </Select>
                    </FormControl>
                }
                { this.state.type == 'recents' &&
                <TextField type="number" 
                    name="day_boundary"
                    // className="full-width"
                    label="Added Since (days)"
                    value={this.state.day_boundary}
                    onChange={this.handleInputChange}></TextField>
                }
                { this.state.type == 'recents' &&
                <FormControlLabel
                    control={
                    <Checkbox checked={this.state.add_this_month} onChange={this.handleThisMonthChange} />
                    }
                    label="This Month"
                />
                }
                { this.state.type == 'recents' &&
                <FormControlLabel
                    control={
                    <Checkbox checked={this.state.add_last_month} onChange={this.handleLastMonthChange} />
                    }
                    label="Last Month"
                />
                }
                <FormControl variant="filled">
                    <InputLabel htmlFor="type-select">Type</InputLabel>
                    <Select
                    native
                    value={this.state.type}
                    onChange={this.handleInputChange}
                    inputProps={{
                        name: 'type',
                        id: 'type-select',
                    }}
                    >
                        <option value="default">Default</option>
                        <option value="recents">Recents</option>
                        <option value="fmchart">Last.fm Chart</option>
                    </Select>
                </FormControl>
                <Button onClick={this.handleRun} variant="contained" color="primary">Run</Button>
            </Card>
            </ThemeProvider>
        );

        return this.state.isLoading ? <CircularProgress /> : table;
    }

}

function ReferenceEntry(props) {
    return <option value={props.name}>{props.name}</option>;
}

function ListBlock(props) {
    return props.list.map((part) => <Row part={ part } key={ part } handler={props.handler}/>);
}

function Row (props) {
    return (
        <tr>
            <td className="ui-text center-text text-no-select">{ props.part }</td>
            <td>
                <IconButton aria-label="delete" onClick={(e) => props.handler(props.part, e)}>
                    <Delete />
                </IconButton>
            </td>
        </tr>
    );
}