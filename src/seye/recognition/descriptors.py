"""Independent bounded geometric descriptors; no learned parameters."""
from seye.interface.regions import edge_mask


def geometry(image):
    image=image.convert('RGB');image.thumbnail((128,128));w,h=image.size
    mask=edge_mask(image);points=[(x,y) for y in range(h) for x in range(w) if mask.getpixel((x,y))]
    mass=len(points);cx=sum(x for x,y in points)/mass if mass else 0;cy=sum(y for x,y in points)/mass if mass else 0
    box=mask.getbbox();area=((box[2]-box[0])*(box[3]-box[1]))/(w*h) if box else 0
    quadrants=[sum((x>=w/2)==bool(i%2) and (y>=h/2)==bool(i//2) for x,y in points)/max(mass,1) for i in range(4)]
    moments=[sum((x-cx)**2 for x,y in points)/max(mass,1)/w**2,
             sum((y-cy)**2 for x,y in points)/max(mass,1)/h**2,
             sum((x-cx)*(y-cy) for x,y in points)/max(mass,1)/(w*h)]
    return [w/(w+h),area,mass/(w*h),cx/w,cy/h]+quadrants+moments


def appearance(image):
    from PIL import Image
    image=image.convert('RGB');image.thumbnail((128,128));pixels=list(image.get_flattened_data());n=len(pixels)
    histogram=[sum(min(p[c]//64,3)==b for p in pixels)/n for c in range(3) for b in range(4)]
    gray=image.convert('L');w,h=gray.size;p=gray.load()
    horizontal=sum(abs(p[x,y]-p[x-1,y]) for y in range(h) for x in range(1,w))/max(1,(w-1)*h)/255
    vertical=sum(abs(p[x,y]-p[x,y-1]) for y in range(1,h) for x in range(w))/max(1,w*(h-1))/255
    layout=[v/255 for v in gray.resize((4,4),Image.Resampling.BOX).get_flattened_data()]
    return histogram+[horizontal,vertical]+layout


def shape(image):
    """Center/crop observed edge support; separate schema from screen layout."""
    from PIL import Image
    image=image.convert('RGB');image.thumbnail((256,256));mask=edge_mask(image);box=mask.getbbox()
    if box is None:return [0.0]*257
    crop=mask.crop(box);w,h=crop.size
    return [v/255 for v in crop.resize((16,16),Image.Resampling.BOX).get_flattened_data()]+[w/(w+h)]
