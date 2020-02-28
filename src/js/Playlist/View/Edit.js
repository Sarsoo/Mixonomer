import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, CircularProgress, FormControl, TextField, InputLabel, Select, Checkbox, FormControlLabel, 
    CardActions, CardContent, Typography, Grid, MenuItem } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';

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


const useStyles = makeStyles({
    root: {
      background: '#9e9e9e',
      color: '#212121'
    },
  });

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
            
            info.data.parts.sort((a, b) => {
                if(a.toLowerCase() < b.toLowerCase()) { return -1; }
                if(a.toLowerCase() > b.toLowerCase()) { return 1; }
                return 0;
            });

            info.data.playlist_references.sort((a, b) => {
                if(a.toLowerCase() < b.toLowerCase()) { return -1; }
                if(a.toLowerCase() > b.toLowerCase()) { return 1; }
                return 0;
            });

            playlists.data.playlists.sort( (a, b) => {
                if(a.name.toLowerCase() < b.name.toLowerCase()) { return -1; }
                if(a.name.toLowerCase() > b.name.toLowerCase()) { return 1; }
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
            <div style={{maxWidth: '1000px', margin: 'auto', marginTop: '20px'}}>
            <Card align="center">
                <CardContent>
                    <Typography variant="h2" color="textPrimary">{this.state.name}</Typography>
                    <Grid container spacing={5}>
                        
                        { this.state.playlist_references.length > 0 && <Grid item xs={12} ><Typography color="textSecondary" variant="h4">Managed</Typography></Grid> }
                        { this.state.playlist_references.length > 0 && <ListBlock handler={this.handleRemoveReference} list={this.state.playlist_references}/> }

                        { this.state.parts.length > 0 && <Grid item xs={12} ><Typography color="textSecondary" variant="h4">Spotify</Typography></Grid> }
                        { this.state.parts.length > 0 && <ListBlock handler={this.handleRemovePart} list={this.state.parts}/> }
                        <Grid item xs={12} ><Typography variant="body2" color="textSecondary">Spotify playlist can be the name of either your own created playlist or one you follow, names are case sensitive</Typography></Grid>
                        <Grid item xs={8} sm={8} md={3}>
                            <TextField
                                name="newPlaylistName"
                                variant="filled"
                                label="Spotify Playlist"
                                value={this.state.newPlaylistName}
                                onChange={this.handleInputChange}
                               
                            />
                        </Grid>
                        <Grid item xs={4} sm={4} md={3}>
                            <Button variant="contained" className="full-width" onClick={this.handleAddPart} style={{verticalAlign: 'middle'}}>Add</Button>
                        </Grid>
                        <Grid item xs={8} sm={8} md={3}>
                            <FormControl variant="filled" style={{verticalAlign: 'middle'}}>
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
                        </Grid>
                        <Grid item xs={4} sm={4} md={3}>
                            <Button variant="contained" className="full-width" onClick={this.handleAddReference} style={{verticalAlign: 'middle'}}>Add</Button>
                        </Grid>
                        <Grid item xs={12}>
                            <FormControlLabel
                                control={
                                <Checkbox color="primary" checked={this.state.shuffle} onChange={this.handleShuffleChange} />
                                }
                                labelPlacement="bottom"
                                label="Shuffle"/>
                            <FormControlLabel
                                control={
                                <Checkbox color="primary" checked={this.state.include_recommendations} onChange={this.handleIncludeRecommendationsChange} />
                                }
                                labelPlacement="bottom"
                                label="Recommendations"/>
                            <FormControlLabel
                                control={
                                <Checkbox color="primary" checked={this.state.include_library_tracks} onChange={this.handleIncludeLibraryTracksChange} />
                                }
                                labelPlacement="bottom"
                                label="Library Tracks"/>
                        </Grid>
                        { this.state.include_recommendations == true &&
                        <Grid item xs={12}>
                            <TextField type="number" 
                                    name="recommendation_sample"
                                    label="Recommendation Size"
                                    variant="filled"
                                    value={this.state.recommendation_sample}
                                    onChange={this.handleInputChange}></TextField>
                        </Grid>
                        }
                        { this.state.type == 'fmchart' &&
                        <Grid item xs={12}>
                            <TextField type="number" 
                                name="chart_limit"
                                label="Chart Size"
                                variant="filled"
                                value={this.state.chart_limit}
                                onChange={this.handleInputChange}></TextField>
                        </Grid>
                        }
                        { this.state.type == 'fmchart' &&
                        <Grid item xs={12}>
                            <FormControl variant="filled">
                                <InputLabel htmlFor="chart_range">Chart Range</InputLabel>
                                <Select
                                value={this.state.chart_range}
                                onChange={this.handleInputChange}
                                inputProps={{
                                    name: "chart_range",
                                    id: "chart_range",
                                }}
                                >
                                    <MenuItem value="WEEK">7 Day</MenuItem>
                                    <MenuItem value="MONTH">30 Day</MenuItem>
                                    <MenuItem value="QUARTER">90 Day</MenuItem>
                                    <MenuItem value="HALFYEAR">180 Day</MenuItem>
                                    <MenuItem value="YEAR">365 Day</MenuItem>
                                    <MenuItem value="OVERALL">Overall</MenuItem>
                                    </Select>
                            </FormControl>
                        </Grid>
                        }
                        { this.state.type == 'recents' &&
                        <Grid item xs={12}>
                            <TextField type="number" 
                                name="day_boundary"
                                // className="full-width"
                                label="Added Since (days)"
                                value={this.state.day_boundary}
                                onChange={this.handleInputChange} />
                        </Grid>
                        }
                        { this.state.type == 'recents' &&
                        <Grid item xs={12}>
                            <FormControlLabel
                                control={
                                <Checkbox color="primary" checked={this.state.add_this_month} onChange={this.handleThisMonthChange} />
                                }
                                label="This Month"
                                labelPlacement="bottom"
                            />
                            <FormControlLabel
                                control={
                                <Checkbox color="primary" checked={this.state.add_last_month} onChange={this.handleLastMonthChange} />
                                }
                                label="Last Month"
                                labelPlacement="bottom"
                            />
                        </Grid>
                        }
                        <Grid item xs={12}>
                            <FormControl variant="filled">
                                <InputLabel htmlFor="type-select">Type</InputLabel>
                                <Select
                                value={this.state.type}
                                onChange={this.handleInputChange}
                                inputProps={{
                                    name: 'type',
                                    id: 'type-select',
                                }}
                                >
                                    <MenuItem value="default">Default</MenuItem>
                                    <MenuItem value="recents">Currents</MenuItem>
                                    <MenuItem value="fmchart">Last.fm Chart</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                    </Grid>
                </CardContent>
                <CardActions>
                    <Button onClick={this.handleRun} variant="contained" color="primary" className="full-width" >Run</Button>
                </CardActions>
            </Card>
        </div>
        );

        return this.state.isLoading ? <CircularProgress /> : table;
    }

}

function ReferenceEntry(props) {
    return <option value={props.name}>{props.name}</option>;
}

function ListBlock(props) {
    return <Grid container 
                spacing={3} 
                direction="row"
                justify="flex-start"
                alignItems="flex-start"
                style={{padding: '24px'}}>
                    {props.list.map((part) => <BlockGridItem part={ part } key={ part } handler={props.handler}/>)}
            </Grid>
}

function BlockGridItem (props) {
    const classes = useStyles();
    return (
        <Grid item xs={12} sm={3} md={2}>
            <Card variant="outlined" className={classes.root}>
                <CardContent>
                    <Typography variant="h5" color="textSecondary" className={classes.root}>{ props.part }</Typography>
                </CardContent>
                <CardActions>
                    <Button className="full-width" color="secondary" variant="contained" aria-label="delete" onClick={(e) => props.handler(props.part, e)} startIcon={<Delete />}>
                        Delete
                    </Button>
                </CardActions>
            </Card>
        </Grid>
    );
}