import React, { Component } from "react";
const axios = require('axios');

import { Card, Grid, Button, TextField, CardContent, CardActions, Typography } from "@material-ui/core";

import showMessage from "../Toast.js"

/**
 * Change password card
 */
class ChangePassword extends Component {
    
    constructor(props){
        super(props);
        this.state = {
            current: "",
            new1: "",
            new2: ""
        }
        this.handleCurrentChange = this.handleCurrentChange.bind(this);
        this.handleNewChange = this.handleNewChange.bind(this);
        this.handleNew2Change = this.handleNew2Change.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    /**
     * Handle current pw state change
     * @param {*} event Event data
     */
    handleCurrentChange(event){
        this.setState({
            'current': event.target.value
        });
    }

    /**
     * Handle new pw state change
     * @param {*} event Event data
     */
    handleNewChange(event){
        this.setState({
            'new1': event.target.value
        });
    }

    /**
     * Handle new again pw state change
     * @param {*} event Event data
     */
    handleNew2Change(event){
        this.setState({
            'new2': event.target.value
        });
    }

    /**
     * Handle submit button click, validate input, make network request
     * @param {*} event Event data
     */
    handleSubmit(event){

        if(this.state.current.length == 0){
            showMessage("enter current password");
        }else{
            if(this.state.new1.length == 0){
                showMessage("enter new password");
            }else{
                if(this.state.new1 != this.state.new2){
                showMessage("new password mismatch");
                }else{
                    axios.post('/api/user/password',{
                        current_password: this.state.current,
                        new_password: this.state.new1
                    }).then((response) => {
                    showMessage("password changed");
                    }).catch((error) => {
                        showMessage(`error changing password (${error.response.status})`);
                    });
                }
            }            
        }

        event.preventDefault();

    }

    render(){
        return (
            <div style={{maxWidth: '500px', margin: 'auto', marginTop: '20px'}}>
                <Card align="center">
                    <form onSubmit={this.handleSubmit}>
                        <CardContent>
                            <Grid container spacing={2}>

                                {/* TITLE */}
                                <Grid item className="full-width">
                                    <Typography variant="h4" color="textPrimary">Change Password</Typography>
                                </Grid>

                                {/* CURRENT PASSWORD */}
                                <Grid item className="full-width">
                                    <TextField
                                        label="Current Password" 
                                        type="password" 
                                        variant="outlined" 
                                        onChange={this.handleCurrentChange}
                                        name="current"
                                        value={this.state.current}
                                        className="full-width" />
                                </Grid>

                                {/* NEW PASSWORD */}
                                <Grid item className="full-width">
                                    <TextField
                                        label="New Password" 
                                        variant="outlined" 
                                        type="password" 
                                        onChange={this.handleNewChange}
                                        name="new1"
                                        value={this.state.new1} 
                                        className="full-width" />
                                </Grid>

                                {/* NEW PASSWORD 2 */}
                                <Grid item className="full-width">
                                    <TextField
                                        label="New Password Again" 
                                        variant="outlined" 
                                        type="password" 
                                        onChange={this.handleNew2Change}
                                        name="new2"
                                        value={this.state.new2}
                                        className="full-width" />
                                </Grid>

                                {/* ERROR MESSAGE */}
                                { this.state.error && <Grid item><Typography variant="textSeondary">{this.state.errorValue}</Typography></Grid>}
                            </Grid>
                        </CardContent>
                        
                        {/* SUBMIT BUTTON */}
                        <CardActions>
                            <Button color="secondary" type="submit" variant="contained" className="full-width" onClick={this.runStats}>Change</Button>
                        </CardActions>
                    </form>
                </Card>
            </div>
        );
    }
}

export default ChangePassword;