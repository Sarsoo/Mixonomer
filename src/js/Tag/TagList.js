import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, ButtonGroup, Typography, Card, CardActions, CardContent, Grid } from '@material-ui/core';

const axios = require('axios');

import showMessage from "../Toast.js"
import Progress from "../Util/circularProgress.js"

/**
 * Tag card list component
 */
class TagList extends Component {

    constructor(props){
        super(props);
        this.state = {
            isLoading: true
        }
        this.getTags();
        this.handleDeleteTag = this.handleDeleteTag.bind(this);
    }

    /**
     * Get tags info from API 
     */
    getTags(){
        var self = this;
        axios.get('/api/tag')
        .then((response) => {

            var tags = response.data.tags.slice();

            tags.sort(function(a, b){
                if(a.name.toLowerCase() < b.name.toLowerCase()) { return -1; }
                if(a.name.toLowerCase() > b.name.toLowerCase()) { return 1; }
                return 0;
            });

            self.setState({
                tags: tags,
                isLoading: false
            });
        })
        .catch((error) => {
            showMessage(`Error Getting Tags (${error.response.status})`);
        });
    }

    /**
     * Make delete tag request of API
     * @param {*} tag_id Tag ID
     * @param {*} event Event Data
     */
    handleDeleteTag(tag_id, event){
        axios.delete(`/api/tag/${tag_id}`)
        .then((response) => {
            showMessage(`${tag_id} Deleted`);
            this.getTags();
        }).catch((error) => {
            showMessage(`Error Deleting ${tag_id} (${error.response.status})`);
        });
    }

    render() {

        const grid =   <TagGrid tags={this.state.tags}
                            handleDeleteTag={this.handleDeleteTag}/>;

        return this.state.isLoading ? <Progress /> : grid;
    }
}

/**
 * Tag card grid component
 * @param {*} props Properties 
 * @returns Grid component
 */
function TagGrid(props){
    return (
        <Grid container
                spacing={3}
                direction="row"
                justifyContent="flex-start"
                alignItems="flex-start"
                style={{padding: '24px'}}>
            <Grid item xs={12} sm={6} md={2}>

                {/* NEW BUTTON */}
                <ButtonGroup
                    color="primary"
                    orientation="vertical"
                    className="full-width">
                    <Button component={Link} to='tags/new' >New</Button>
                </ButtonGroup>
            </Grid>

            {/* TAG CARDS */}
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

/**
 * Tag card component
 * @param {*} props Properties
 * @returns Card component
 */
function TagCard(props){
    return (
        <Grid item xs>
            <Card className="card">
                <CardContent>

                    {/* TAG NAME */}
                    <Typography variant="h4" component="h2">
                    { props.tag.name }
                    </Typography>

                    {/* COUNT */}
                    {'count' in props.tag && 
                        <Typography variant="h6" style={{color: "#b3b3b3"}}>
                            { props.tag.count.toLocaleString("en-GB") }
                        </Typography>
                    }
                </CardContent>
                <CardActions>
                    <ButtonGroup
                    color="secondary"
                    variant="contained">

                        {/* VIEW BUTTON */}
                        <Button component={Link} to={getTagLink(props.tag.tag_id)}>View</Button>

                        {/* DELETE BUTTON */}
                        <Button onClick={(e) => props.handleDeleteTag(props.tag.tag_id, e)}>Delete</Button>
                    </ButtonGroup>
                </CardActions>
            </Card>
        </Grid>
    );
}

/**
 * Map tag name to URL
 * @param {*} tagName Subject tag name
 * @returns Tag URL
 */
function getTagLink(tagName){
    return `/app/tag/${tagName}`;
}

export default TagList;