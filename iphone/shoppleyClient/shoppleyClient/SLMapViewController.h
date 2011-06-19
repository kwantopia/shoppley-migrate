//
//  SLMapViewController.h
//  shoppleyClient
//
//  Created by yod on 6/19/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <MapKit/MapKit.h>

@interface SLMapViewController : TTViewController <MKMapViewDelegate> {
    double _latitude;
    double _longitude;
    NSString* _mTitle;
    NSString* _mSubtitle;
}

- (id)initWithLatitude:(NSString*)latitude longitude:(NSString*)longitude title:(NSString*)title;
- (id)initWithLatitude:(NSString*)latitude longitude:(NSString*)longitude title:(NSString*)title subtitle:(NSString*)subtitle;

@end
