#!/usr/bin/env python3
import boto3
import json
import time
import sys
from datetime import datetime, timedelta

def extract_logs(log_group_name, minutes=30, output_file="recent_logs.txt", profile_name="anova", region="us-east-1"):
    """
    Extract logs from the specified CloudWatch log group for the last X minutes,
    excluding any "GET / HTTP/1.1" 200 OK" entries.
    
    Args:
        log_group_name (str): The name of the CloudWatch log group
        minutes (int): Number of minutes to look back
        output_file (str): Name of the output file
        profile_name (str): AWS profile name
        region (str): AWS region
    """
    print(f"Extracting logs from {log_group_name} for the last {minutes} minutes...")
    
    # Create a session using the specified profile
    session = boto3.Session(profile_name=profile_name, region_name=region)
    logs_client = session.client('logs')
    
    # Calculate the start time (X minutes ago)
    start_time = int((datetime.now() - timedelta(minutes=minutes)).timestamp() * 1000)
    
    # Get all log streams
    try:
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True
        )
    except Exception as e:
        print(f"Error getting log streams: {e}")
        sys.exit(1)
    
    log_streams = response.get('logStreams', [])
    if not log_streams:
        print(f"No log streams found in {log_group_name}")
        sys.exit(1)
    
    print(f"Found {len(log_streams)} log streams. Extracting logs...")
    
    # Open the output file
    with open(output_file, 'w') as f:
        f.write(f"Logs from {log_group_name} for the last {minutes} minutes\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        total_events = 0
        filtered_events = 0
        
        # Process each log stream
        for stream in log_streams:
            stream_name = stream['logStreamName']
            f.write(f"Log Stream: {stream_name}\n")
            f.write("-" * 80 + "\n")
            
            # Get log events from this stream
            try:
                events = []
                next_token = None
                
                while True:
                    if next_token:
                        response = logs_client.get_log_events(
                            logGroupName=log_group_name,
                            logStreamName=stream_name,
                            startTime=start_time,
                            startFromHead=False,
                            nextToken=next_token
                        )
                    else:
                        response = logs_client.get_log_events(
                            logGroupName=log_group_name,
                            logStreamName=stream_name,
                            startTime=start_time,
                            startFromHead=False
                        )
                    
                    # Process events
                    for event in response['events']:
                        total_events += 1
                        message = event['message']
                        timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Skip "GET / HTTP/1.1" 200 OK" entries and other successful GET requests
                        if 'GET /' in message and '" 200 OK' in message:
                            continue
                        
                        # Highlight errors and warnings
                        if 'error' in message.lower() or 'exception' in message.lower() or 'warning' in message.lower() or 'fail' in message.lower() or '" 4' in message or '" 5' in message:
                            message = f"!!! ERROR/WARNING: {message}"
                            
                        filtered_events += 1
                        f.write(f"[{timestamp}] {message}\n")
                    
                    # Check if we need to continue pagination
                    if next_token == response['nextForwardToken']:
                        break
                    next_token = response['nextForwardToken']
                    
                    # If no events in this batch, we can stop
                    if not response['events']:
                        break
                    
            except Exception as e:
                f.write(f"Error getting logs from stream {stream_name}: {e}\n")
                continue
                
            f.write("\n")
        
        # Write summary
        f.write("=" * 80 + "\n")
        f.write(f"Summary: Processed {total_events} events, filtered to {filtered_events} events\n")
    
    print(f"Logs extracted to {output_file}")
    print(f"Processed {total_events} events, filtered to {filtered_events} events")

if __name__ == "__main__":
    # Default values
    log_group_name = "/ecs/basketball-analysis"
    minutes = 30
    output_file = "recent_logs.txt"
    profile_name = "anova"
    region = "us-east-1"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        log_group_name = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            minutes = int(sys.argv[2])
        except ValueError:
            print(f"Invalid minutes value: {sys.argv[2]}. Using default: {minutes}")
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    if len(sys.argv) > 4:
        profile_name = sys.argv[4]
    if len(sys.argv) > 5:
        region = sys.argv[5]
    
    extract_logs(log_group_name, minutes, output_file, profile_name, region)
