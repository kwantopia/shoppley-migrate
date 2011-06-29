//
//  SLMapViewController.m
//  shoppleyClient
//
//  Created by yod on 6/19/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLMapViewController.h"

static CLLocationDegrees kLatitudeDelta = 0.02;
static CLLocationDegrees kLongitudeDelta = 0.02;

#pragma mark -
#pragma mark AddressAnnotation

@interface AddressAnnotation : NSObject <MKAnnotation> {
    CLLocationCoordinate2D _coordinate;
    NSString* _title;
    NSString* _subtitle;
}

@end

@implementation AddressAnnotation

@synthesize coordinate = _coordinate;

- (void)dealloc {
    TT_RELEASE_SAFELY(_title);
    TT_RELEASE_SAFELY(_subtitle);
    [super dealloc];
}

- (NSString*)title {
    return _title;
}

- (NSString*)subtitle {
    return _subtitle;
}

- (id)initWithCoordinate:(CLLocationCoordinate2D)coordinate title:(NSString*)title subtitle:(NSString*)subtitle {
    _coordinate = coordinate;
    _title = [title retain];
    _subtitle = [subtitle retain];
    return self;
}

@end

#pragma mark -
#pragma mark SLMapViewController

@implementation SLMapViewController

- (id)initWithLatitude:(NSString*)latitude longitude:(NSString*)longitude title:(NSString*)title {
    return [self initWithLatitude:latitude longitude:longitude title:title subtitle:@""];
}

- (id)initWithLatitude:(NSString*)latitude longitude:(NSString*)longitude title:(NSString*)title subtitle:(NSString*)subtitle {
    if ((self = [self init])) {
        self.title = [title stringByReplacingOccurrencesOfString:@"_" withString:@" "];
        
        _latitude = [latitude doubleValue];
        _longitude = [longitude doubleValue];
        _mTitle = [self.title retain];
        _mSubtitle = [subtitle retain];
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_mTitle);
    TT_RELEASE_SAFELY(_mSubtitle);
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    CGRect mapRect = CGRectMake(self.view.bounds.origin.x, self.view.bounds.origin.y, self.view.bounds.size.width, self.view.bounds.size.height - 44.0f);
    MKMapView *mapView = [[[MKMapView alloc] initWithFrame:mapRect  ] autorelease];
    mapView.delegate = self;
    
    // Region and Zoom    
    MKCoordinateSpan span = MKCoordinateSpanMake(kLatitudeDelta, kLongitudeDelta);
    CLLocationCoordinate2D location = CLLocationCoordinate2DMake(_latitude, _longitude);
    MKCoordinateRegion region = MKCoordinateRegionMake(location, span);
    [mapView setRegion:region animated:TRUE];
    [mapView regionThatFits:region];
    
    AddressAnnotation *addressAnnotation = [[[AddressAnnotation alloc] initWithCoordinate:location title:_mTitle subtitle:_mSubtitle] autorelease];    
    [mapView addAnnotation:addressAnnotation];
    [self.view addSubview:mapView];
    
    self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Open in Maps" style:UIBarButtonItemStylePlain target:self action:@selector(openInMaps)] autorelease];
}

# pragma mark <MKMapViewDelegate>

- (void)mapViewDidFinishLoadingMap:(MKMapView *)mapView {
    [mapView selectAnnotation:[[mapView annotations] lastObject] animated:YES];
}

- (void)openInMaps {
    [[UIApplication sharedApplication] openURL:[NSURL URLWithString:[NSString stringWithFormat:@"http://maps.google.com/maps?q=%.4f,%.4f+(%@)", _latitude, _longitude, [_mTitle stringByReplacingOccurrencesOfString:@" " withString:@"+"]]]];
}

@end
