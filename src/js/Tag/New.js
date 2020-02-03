import React, { Component } from "react";
const axios = require('axios');

import { Card, Button, TextField, CardActions, CardContent, Typography, Grid } from '@material-ui/core';

import showMessage from "../Toast.js"

class NewTag extends Component {

    constructor(props) {
        super(props);
        this.state = {
            tag_id: ''
        }
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event){
        this.setState({
            tag_id: event.target.value
        });
    }

    handleSubmit(event){
        var tag_id = this.state.tag_id;
        this.setState({
            tag_id: ''
        });

        if(tag_id.length != 0){
            axios.get('/api/tag')
            .then((response) => {
                var tag_ids = response.data.tags.map(entry => entry.tag_id)

                var sameTag_id = tag_ids.includes(this.state.tag_id);
                if(sameTag_id == false){
                    axios.post(`/api/tag/${tag_id}`).then((response) => {
                        showMessage(`${tag_id} Created`);
                    }).catch((error) => {
                        showMessage(`Error Creating Tag (${error.response.status})`);
                    });
                }else{
                    showMessage('Named Tag Already Exists');
                }
            })
            .catch((error) => {
                showMessage(`Error Getting Tags (${error.response.status})`);
            });
        }else{
            showMessage('Enter Name');
        }
    }

    render(){
        return (
            <div style={{maxWidth: '500px', margin: 'auto', marginTop: '20px'}}>
            <Card align="center">
                <CardContent>
                    <Grid container spacing={5}>
                        <Grid item xs={12}>
                            <Typography variant="h3">New Tag</Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                label="Name" 
                                variant="outlined" 
                                onChange={this.handleInputChange}
                                name="tag_id"
                                value={this.state.tag_id} 
                                className="full-width" />
                        </Grid>
                    </Grid>
                </CardContent>
                <CardActions>
                    <Button variant="contained" color="primary" className="full-width" onClick={this.handleSubmit}>Create</Button>
                </CardActions>
            </Card>
            </div>
        );
    }

}

export default NewTag;