import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, ButtonGroup, Typography, Card, Grid, CircularProgress } from '@material-ui/core';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
const axios = require('axios');

import showMessage from "../Toast.js"

class TagList extends Component {

    constructor(props){
        super(props);
        this.state = {
            isLoading: true
        }
        this.getTags();
        this.handleRunTag = this.handleRunTag.bind(this);
        this.handleDeleteTag = this.handleDeleteTag.bind(this);
        this.handleRunAll = this.handleRunAll.bind(this);
    }

    getTags(){
        var self = this;
        axios.get('/api/tags')
        .then((response) => {

            var tags = response.data.tags.slice();

            tags.sort(function(a, b){
                if(a.name.toLowerCase() < b.name.toLowerCase()) { return -1; }
                if(a.name.toLowerCase() > b.name.toLowerCase()) { return 1; }
                return 0;
            });

            self.setState({
                playlists: tags,
                isLoading: false
            });
        })
        .catch((error) => {
            showMessage(`Error Getting Playlists (${error.response.status})`);
        });
    }

    handleRunTag(name, event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.spotify_linked == true){
                axios.get('/api/tag/run', {params: {name: name}})
                .then((response) => {
                    showMessage(`${name} ran`);
                })
                .catch((error) => {
                    showMessage(`Error Running ${name} (${error.response.status})`);
                });
            }else{
                showMessage(`Link Spotify Before Running`);
            }
        }).catch((error) => {
            showMessage(`Error Running ${this.state.name} (${error.response.status})`);
        });
    }

    handleDeleteTag(name, event){
        axios.delete('/api/playlist', { params: { name: name } })
        .then((response) => {
            showMessage(`${name} Deleted`);
            this.getTags();
        }).catch((error) => {
            showMessage(`Error Deleting ${name} (${error.response.status})`);
        });
    }

    handleRunAll(event){
        axios.get('/api/user')
        .then((response) => {
            if(response.data.spotify_linked == true){
                axios.get('/api/tag/run/user')
                .then((response) => {
                    showMessage("All Tags Ran");
                })
                .catch((error)  => {
                    showMessage(`Error Running All (${error.response.status})`);
                });
            }else{
                showMessage(`Link Spotify Before Running`);
            }
        }).catch((error) => {
            showMessage(`Error Running ${this.state.name} (${error.response.status})`);
        });
    }

    render() {

        const grid =   <TagGrid tags={this.state.tags}
                            handleRunTag={this.handleRunTag}
                            handleDeleteTag={this.handleDeleteTag}
                            handleRunAll={this.handleRunAll}/>;

        return this.state.isLoading ? <CircularProgress /> : grid;
    }
}

function TagGrid(props){
    return (
        <Grid container
                spacing={3}
                direction="row"
                justify="flex-start"
                alignItems="flex-start"
                style={{padding: '24px'}}>
            <Grid item xs>
                <ButtonGroup
                    color="primary"
                    orientation="vertical"
                    className="full-width">
                    <Button component={Link} to='tags/new' >New</Button>
                    <Button onClick={props.handleRunAll}>Run All</Button>
                </ButtonGroup>
            </Grid>
            { props.tags.length == 0 ? (
                <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="h5" component="h2">No Tags</Typography>
                </Grid>
            ) : (
                props.tags.map((tag) => <TagCard tag={ tag }
                                                handleRunTag={props.handleRunTag}
                                                handleDeleteTag={props.handleDeleteTag}
                                                key={ tag.name }/>)
            )}
        </Grid>
    );
}

function TagCard(props){
    return (
        <Grid item xs>
            <Card>
                <CardContent>
                    <Typography variant="h5" component="h2">
                    { props.tag.name }
                    </Typography>
                </CardContent>
                <CardActions>
                    <ButtonGroup
                    color="primary"
                    variant="contained">
                        <Button component={Link} to={getTagLink(props.tag.name)}>View</Button>
                        <Button onClick={(e) => props.handleRunTag(props.tag.name, e)}>Update</Button>
                        <Button onClick={(e) => props.handleDeleteTag(props.tag.name, e)}>Delete</Button>
                    </ButtonGroup>
                </CardActions>
            </Card>
        </Grid>
    );
}

function getTagLink(tagName){
    return `/app/tag/${tagName}/edit`;
}

export default TagList;