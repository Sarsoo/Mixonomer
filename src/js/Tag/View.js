import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, CircularProgress, CardActions, CardContent, FormControl, InputLabel, Select, Typography, Grid, TextField, MenuItem, FormControlLabel, Switch } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';

import showMessage from "../Toast.js";

const BarChart = React.lazy(() => import("../Maths/BarChart"))
const PieChart = React.lazy(() => import("../Maths/PieChart"))

const useStyles = makeStyles({
    root: {
      background: '#9e9e9e',
      color: '#212121',
      align: "center"
    },
  });

/**
 * Tag View card
 */
class TagView extends Component{

    constructor(props){
        super(props);
        this.state = {
            tag_id: props.match.params.tag_id,
            tag: {
                name: "",
                tracks: [],
                albums: [],
                artists: []
            },

            addType: 'artists',

            name: '',
            artist: '',

            isLoading: true
        }
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleRun = this.handleRun.bind(this);
        this.handleRemoveObj = this.handleRemoveObj.bind(this);

        this.handleCheckChange = this.handleCheckChange.bind(this);
        this.makeNetworkUpdate = this.makeNetworkUpdate.bind(this);

        this.handleAdd = this.handleAdd.bind(this);
        this.handleChangeAddType = this.handleChangeAddType.bind(this);
    }

    /**
     * Get tag info from API on load
     */
    componentDidMount(){
        this.getTag();
        // var intervalId = setInterval(() => {this.getTag(false)}, 5000);
        // var timeoutId = setTimeout(() => {clearInterval(this.state.intervalId)}, 300000);

        // this.setState({
        //     intervalId: intervalId,
        //     timeoutId: timeoutId
        // });
    }

    // componentWillUnmount(){
    //     clearInterval(this.state.intervalId);
    //     clearTimeout(this.state.timeoutId);
    // }

    /**
     * Get tag info from API
     * @param {*} error_toast Whether to show toast on network error 
     */
    getTag(error_toast = true){
        axios.get(`/api/tag/${ this.state.tag_id }`)
        .then( (response) => {

            var tag = response.data.tag;

            tag.artists = tag.artists.sort((a, b) => {
                if(a.name.toLowerCase() < b.name.toLowerCase()) { return -1; }
                if(a.name.toLowerCase() > b.name.toLowerCase()) { return 1; }
                return 0;
            });

            tag.albums = tag.albums.sort((a, b) => {
                if(a.artist.toLowerCase() < b.artist.toLowerCase()) { return -1; }
                if(a.artist.toLowerCase() > b.artist.toLowerCase()) { return 1; }
                return 0;
            });

            tag.tracks = tag.tracks.sort((a, b) => {
                if(a.artist.toLowerCase() < b.artist.toLowerCase()) { return -1; }
                if(a.artist.toLowerCase() > b.artist.toLowerCase()) { return 1; }
                return 0;
            });

            this.setState({
                tag: response.data.tag,
                isLoading: false
            });
        })
        .catch( (error) => {
            if(error_toast) {
                showMessage(`Error Getting Tag Info (${error.response.status})`);
            }
        });
    }

    /**
     * Handle input box state changes
     * @param {*} event Event data
     */
    handleInputChange(event){
        
        this.setState({
            [event.target.name]: event.target.value
        });

    }

    /**
     * Handle checkbox state changes, make network updates
     * @param {*} event Event data
     */
    handleCheckChange(event){
        let payload = {...this.state.tag};
        payload[event.target.name] = event.target.checked;
        
        this.setState({tag: payload});

        switch(event.target.name){
            default:
                this.makeNetworkUpdate({[event.target.name]: event.target.checked});
        }
    }

    /**
     * Put tag info changes to API
     * @param {*} changes Dictionary of changes to submit
     */
    makeNetworkUpdate(changes){
        axios.put(`/api/tag/${this.state.tag_id}`, changes).catch((error) => {
            showMessage(`Error updating ${Object.keys(changes).join(", ")} (${error.response.status})`);
        });
    }

    /**
     * Validate input and make tag refresh update of API
     * @param {*} event 
     */
    handleRun(event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.lastfm_username != null){
                axios.get(`/api/tag/${this.state.tag_id}/update`)
                .then((reponse) => {
                    showMessage(`${this.state.name} Updating`);
                })
                .catch((error) => {
                    showMessage(`Error Updating ${this.state.tag_id} (${error.response.status})`);
                });
            }else{
                showMessage(`Add a Last.fm Username In Settings`);
            }
        }).catch((error) => {
            showMessage(`Error Updating ${this.state.tag_id} (${error.response.status})`);
        });
    }

    /**
     * Handle remove watched part
     * @param {*} music_obj Subject object to remove
     * @param {*} addType Object type (tracks/albums/artists)
     * @param {*} event Event data
     */
    handleRemoveObj(music_obj, addType, event){
        var startingItems = this.state.tag[addType].slice();

        var items = this.state.tag[addType].slice();
        items = items.filter((item) => {
            if(addType == 'albums' || addType == 'tracks') {
                return item.name.toLowerCase() != music_obj.name.toLowerCase() || item.artist.toLowerCase() != music_obj.artist.toLowerCase();
            }else{
                return item.name.toLowerCase() != music_obj.name.toLowerCase();
            }
        });

        var tag = this.state.tag;
        tag[addType] = items;

        this.setState({
            tag: tag
        });

        axios.put(`/api/tag/${this.state.tag_id}`, {
            [addType]: items
        })
        .catch( (error) => {
            showMessage(`Error Removing ${music_obj.name} (${error.response.status})`);

            redo_tag[addType] = startingItems;
            this.setState({
                tag: redo_tag
            });
        });
    }

    /**
     * Handle adding type drop down change
     * @param {*} type 
     */
    handleChangeAddType(type){
        this.setState({
            addType: type
        })
    }

    /**
     * Validate input, make tag part add request of API
     * @returns Nothing
     */
    handleAdd(){

        var addType = this.state.addType;
        var music_obj = {
            name: this.state.name,
            artist: this.state.artist
        }

        if(music_obj.name == ''){
            showMessage(`Enter Name`);
            return;
        }

        if(music_obj.artist == '' && addType != 'artists'){
            showMessage(`Enter Artist`);
            return;
        }

        var list = this.state.tag[addType].slice().filter((item) => {
            if(addType != 'artists') {
                return item.name.toLowerCase() == music_obj.name.toLowerCase() && item.artist.toLowerCase() == music_obj.artist.toLowerCase();
            }else{
                return item.name.toLowerCase() == music_obj.name.toLowerCase();
            }
        });

        if(list.length != 0) {
            showMessage(`${music_obj.name} already present`);
            return;
        } 

        list = this.state.tag[addType].slice();
        if(addType == 'artist'){
            list.push({
                name: music_obj.name
            });
        }else{
            list.push(music_obj);
        }

        if(addType == "artists"){
            list = list.sort((a, b) => {
                if(a.name.toLowerCase() < b.name.toLowerCase()) { return -1; }
                if(a.name.toLowerCase() > b.name.toLowerCase()) { return 1; }
                return 0;
            });
        }else{
            list = list.sort((a, b) => {
                if(a.artist.toLowerCase() < b.artist.toLowerCase()) { return -1; }
                if(a.artist.toLowerCase() > b.artist.toLowerCase()) { return 1; }
                return 0;
            });
        } 

        var tag = this.state.tag;
        tag[addType] = list;

        this.setState({
            tag: tag,
            name: '',
            artist: ''
        });
        
        axios.put(`/api/tag/${this.state.tag_id}`, {
            [addType]: list
        })
        .catch( (error) => {
            showMessage(`Error Adding ${music_obj.name} (${error.response.status})`);
        });
    }

    render(){
        
        var all = [...this.state.tag.artists, ...this.state.tag.albums, ...this.state.tag.tracks];

        var scrobbleData = all.map((entry) => {
            return {
                "label": entry.name,
                "value": entry.count
            };
        }).sort((a, b) => {
            if(a.value < b.value) { return 1; }
            if(a.value > b.value) { return -1; }
            return 0;
        });

        var timeData = all.map((entry) => {
            return {
                "label": entry.name,
                "value": entry.time_ms / (1000 * 60 * 60)
            };
        }).sort((a, b) => {
            if(a.value < b.value) { return 1; }
            if(a.value > b.value) { return -1; }
            return 0;
        });

        const table = (
            <div style={{maxWidth: '1000px', margin: 'auto', marginTop: '20px'}}>
            <Card align="center">
                <CardContent>

                    {/* TAG NAME TITLE */}
                    <Typography variant="h2" color="textPrimary">{this.state.tag.name}</Typography>
                    <Grid container spacing={5}>
                        
                        {/* ARTISTS TITLE */}
                        { this.state.tag.artists.length > 0 && <Grid item xs={12} ><Typography color="textSecondary" variant="h4">Artists</Typography></Grid> }
                        {/* ARTIST CARDS */}
                        { this.state.tag.artists.length > 0 && <ListBlock handler={this.handleRemoveObj} list={this.state.tag.artists} addType="artists" showTime={this.state.tag.time_objects}/> }

                        {/* ALBUMS TITLE */}
                        { this.state.tag.albums.length > 0 && <Grid item xs={12} ><Typography color="textSecondary" variant="h4">Albums</Typography></Grid> }
                        {/* ALBUM CARDS */}
                        { this.state.tag.albums.length > 0 && <ListBlock handler={this.handleRemoveObj} list={this.state.tag.albums} addType="albums" showTime={this.state.tag.time_objects}/> }

                        {/* TRACKS TITLE */}
                        { this.state.tag.tracks.length > 0 && <Grid item xs={12} ><Typography color="textSecondary" variant="h4">Tracks</Typography></Grid> }
                        {/* TRACK CARDS */}
                        { this.state.tag.tracks.length > 0 && <ListBlock handler={this.handleRemoveObj} list={this.state.tag.tracks} addType="tracks" showTime={this.state.tag.time_objects}/> }

                        {/* NAME TEXTBOX */}
                        <Grid item xs={12} sm={this.state.addType != 'artists' ? 3 : 4} md={this.state.addType != 'artists' ? 3 : 4}>
                            <TextField
                                name="name"
                                label="Name"
                                variant="filled"
                                value={this.state.name}
                                onChange={this.handleInputChange}></TextField>
                        </Grid>
                        {/* ARTIST NAME TEXTBOX */}
                        { this.state.addType != 'artists' &&
                        <Grid item xs={12} sm={3} md={4}>
                            <TextField
                                name="artist"
                                label="Artist"
                                variant="filled"
                                value={this.state.artist}
                                onChange={this.handleInputChange}></TextField>
                        </Grid>
                        }

                        {/* ADD TYPE DROPDOWN */}
                        <Grid item xs={12} sm={this.state.addType != 'artists' ? 2 : 4} md={this.state.addType != 'artists' ? 2 : 4}>
                            <FormControl variant="filled">
                                <InputLabel htmlFor="addType">Type</InputLabel>
                                <Select
                                    value={this.state.addType}
                                    onChange={this.handleInputChange}
                                    inputProps={{
                                        name: "addType",
                                        id: "addType",
                                    }}
                                    >
                                    <MenuItem value="artists">Artist</MenuItem>
                                    <MenuItem value="albums">Album</MenuItem>
                                    <MenuItem value="tracks">Track</MenuItem>
                                    </Select>
                            </FormControl>
                        </Grid>

                        {/* ADD BUTTON */}
                        <Grid item xs={12} sm={this.state.addType != 'artists' ? 3 : 4} md={this.state.addType != 'artists' ? 3 : 4}>
                            <Button variant="contained" onClick={this.handleAdd} className="full-width">Add</Button>
                        </Grid>

                        {/* TIME CHECKBOX */}
                        <Grid item xs={12}>
                            <FormControlLabel
                                control={
                                <Switch color="primary" checked={this.state.tag.time_objects} name="time_objects" onChange={this.handleCheckChange} />
                                }
                                label="Time Tag"
                                labelPlacement="bottom"
                            />
                        </Grid>

                        {/* STATS CARD */}
                        <StatsCard count={this.state.tag.count} proportion={this.state.tag.proportion} showTime={this.state.tag.time_objects} time={this.state.tag.total_time}></StatsCard>

                        {/* PIE CHART */}
                        <Grid item xs={12}>
                            <PieChart data={scrobbleData} padding={50}/>
                        </Grid>

                        {/* SCROBBLE BAR CHART */}
                        <Grid item xs={12}>
                            <BarChart data={scrobbleData} title='plays (scrobbles)' indexAxis='y'/>
                        </Grid>

                        {/* TIME BAR CHART */}
                        { this.state.tag.time_objects &&
                        <Grid item xs={12}>
                            <BarChart data={timeData} title='time listened (hours)' indexAxis='y'/>
                        </Grid>
                        }

                        {/* LAST UPDATED */}
                        <Grid item xs={12}>
                            <Typography variant="overline" color="textSecondary">
                                Last Updated: {this.state.tag.last_updated}
                            </Typography>
                        </Grid>
                        
                    </Grid>
                </CardContent>
                {/* UPDATE BUTTON */}
                <CardActions>
                    <Button onClick={this.handleRun} variant="contained" color="primary" className="full-width" >Update</Button>
                </CardActions>
            </Card>
        </div>
        );

        return this.state.isLoading ? <CircularProgress /> : table;
    }    
}

export default TagView;

/**
 * Grid component for holding artist/album/track cards
 * @param {*} props Properties
 * @returns Grid component
 */
function ListBlock(props) {
    return <Grid container 
                spacing={3} 
                direction="row"
                justify="flex-start"
                alignItems="flex-start"
                style={{padding: '24px'}}>
                    {props.list.map((music_obj) => <BlockGridItem music_obj={ music_obj } key={ music_obj.name } 
                                                        handler={ props.handler } addType={ props.addType } showTime={ props.showTime }/>)}
            </Grid>
}

/**
 * Track/album/artist card with time info and delete button
 * @param {*} props Properties
 * @returns Card component wrapped in grid cell
 */
function BlockGridItem (props) {
    const classes = useStyles();
    return (
        <Grid item xs={12} sm={4} md={3}>
            <Card variant="outlined" className={classes.root}>
                <CardContent>
                    <Grid>

                        {/* NAME TITLE */}
                        <Grid item xs={12}>
                            <Typography variant="h4" color="textSecondary" className={classes.root}>{ props.music_obj.name }</Typography>
                        </Grid>

                        {/* ARTIST NAME */}
                        { 'artist' in props.music_obj &&
                            <Grid item xs={12}>
                                <Typography variant="body1" color="textSecondary" className={classes.root}>{ props.music_obj.artist }</Typography>
                            </Grid>
                        }

                        {/* SCROBBLE COUNT */}
                        { 'count' in props.music_obj &&
                            <Grid item xs={8}>
                                <Typography variant="h4" color="textPrimary" className={classes.root}>📈 { props.music_obj.count.toLocaleString("en-GB") }</Typography>
                            </Grid>
                        }
                        {/* TIME */}
                        { 'time' in props.music_obj && props.showTime &&
                            <Grid item xs={8}>
                                <Typography variant="body1" color="textSecondary" className={classes.root}>🕒 { props.music_obj.time }</Typography>
                            </Grid>
                        }
                    </Grid>
                </CardContent>

                {/* DELETE BUTTON */}
                <CardActions>
                    <Button className="full-width" color="secondary" variant="contained" aria-label="delete" onClick={(e) => props.handler(props.music_obj, props.addType, e)} startIcon={<Delete />}>
                        Delete
                    </Button>
                </CardActions>
            </Card>
        </Grid>
    );
}

/**
 * Stats card component with total time and scrobbles
 * @param {*} props Properties
 * @returns Card component wrapped in grid cell
 */
function StatsCard (props) {
    const classes = useStyles();
    return (
        <Grid item xs={12}>
            <Card variant="outlined" className={classes.root}>
                <CardContent>
                    <Grid container spacing={10}>
                        
                        {/* SCROBBLE COUNT */}
                        <Grid item xs={12}>
                            <Typography variant="h1" color="textPrimary" className={classes.root}>📈 { props.count.toLocaleString("en-GB") }</Typography>
                        </Grid>

                        {/* PERCENT */}
                        <Grid item xs={12}>
                            <Typography variant="h4" color="textSecondary" className={classes.root}>{ props.proportion.toFixed(2) }%</Typography>
                        </Grid>

                        {/* TOTAL TIME */}
                        {props.showTime &&
                            <Grid item xs={12}>
                                <Typography variant="h4" color="textSecondary" className={classes.root}>🕒 { props.time }</Typography>
                            </Grid>
                        }
                    </Grid>
                </CardContent>
            </Card>
        </Grid>
    );
}
